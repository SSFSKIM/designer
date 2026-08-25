/**
 * The dev playground, and C9's showpiece skeleton.
 *
 * Structure and semantics live here; every visual decision lives in
 * `styles.css`, so restyling this into the public showpiece is CSS-level work.
 *
 * What it exercises, in the order the parent acceptance lists them:
 *
 *  - **#1** an ordinary React tree wrapped in `GlassRoot`, with real DOM controls
 *    over ordinary page content: selectable prose behind the glass, buttons that
 *    are `<button>`s, a toolbar that is a toolbar.
 *  - **#2** the texture upgrade: the right-hand region registers its own canvas
 *    as a GPU-ownable backdrop, so where WebGPU is available its glass genuinely
 *    bends the bands behind it, and the larger plate lenses harder than the small
 *    one over the same backdrop.
 *  - **#3** press feedback on every control, driven by the interaction machine.
 *  - **#4** the toolbar's Actions button morphing into a menu platter on the
 *    overlay plane.
 *  - **#5** honest degradation: the same page on a browser with no WebGPU — or
 *    with the renderer chunk unreachable — renders presentable CSS-tier glass,
 *    and the panel names the demotion instead of hiding it.
 *  - **#6** the accessibility policy, overridable from the panel, and the
 *    variant-mixing warning on demand.
 *
 * Both backdrop modes are on screen at once: the left region is arbitrary DOM,
 * the right is a registered texture source. The panel reports what each group
 * actually resolved to.
 *
 * ## Why the page does not scroll
 *
 * X1 puts glass in viewport-fixed planes and documents arbitrary interleaving
 * with foreign stacking contexts out of contract for v1. A scrolling page would
 * therefore slide out from under its own glass. The playground is composed to fit
 * the viewport instead of pretending otherwise.
 */

import {
  DEFAULT_CLEAR_DIMMING,
  GlassButton,
  GlassGroup,
  GlassIconButton,
  GlassRoot,
  GlassSegmentedControl,
  GlassSurface,
  GlassToolbar,
  PlanePortal,
} from "@vitreajs/vitrea-react";
import { useState, type ReactNode } from "react";

import { ActionsMenu } from "./ActionsMenu";
import { CapabilitiesPanel, type OverrideState } from "./CapabilitiesPanel";
import { TextureBackdrop } from "./TextureBackdrop";

const TEXTURE_SOURCE = { kind: "texture", id: "playground.canvas" } as const;

const GROUPS = [
  { id: "dom-region", label: "dom-region (arbitrary DOM)" },
  { id: "texture-region", label: "texture-region (registered texture)" },
  { id: "toolbar", label: "toolbar" },
  { id: "toolbar-menu", label: "toolbar-menu (the morph)" },
] as const;

const RANGES = [
  { value: "day", label: "Day" },
  { value: "week", label: "Week" },
  { value: "month", label: "Month" },
] as const;

type Range = (typeof RANGES)[number]["value"];

/**
 * Which tier to ask for, from `?renderer=css|webgpu`. Defaults to the GPU tier.
 *
 * A playground whose renderer cannot be pinned can only be seen on whatever the
 * visiting browser happens to offer, and the two tiers are meant to be compared
 * — that is what the resolved-state panel is for. It also gives a test suite
 * about CSS-tier declarations a way to say so: once both tiers exist, "read the
 * host's backdrop-filter" is a question that needs to name which renderer it
 * expects to have written it.
 *
 * Read once at module scope: the renderer is a `GlassRoot` construction-time
 * choice, so changing it means a reload, which is exactly what editing the URL
 * does.
 */
const REQUESTED_RENDERER: "css" | "webgpu" =
  new URLSearchParams(window.location.search).get("renderer") === "css" ? "css" : "webgpu";

export function App(): ReactNode {
  const [overrides, setOverrides] = useState<OverrideState>({
    reducedMotion: "system",
    reducedTransparency: "system",
    increasedContrast: "system",
  });
  const [variantMixed, setVariantMixed] = useState(false);
  const [range, setRange] = useState<Range>("week");
  const [lastAction, setLastAction] = useState<string | null>(null);
  const [favorite, setFavorite] = useState(false);

  return (
    <GlassRoot
      // Asking is not getting: where there is no adapter, no device, or no
      // renderer, every group resolves to the CSS tier and the panel below says
      // so by name. That is acceptance #5, and it is why asking for the GPU tier
      // by default is safe to ship.
      renderer={REQUESTED_RENDERER}
      reducedMotion={overrides.reducedMotion}
      reducedTransparency={overrides.reducedTransparency}
      increasedContrast={overrides.increasedContrast}
    >
      {/* The page: ordinary DOM, and it stays ordinary DOM. */}
      <main className="page">
        <section className="region region--dom">
          <p className="region__label">backdrop: arbitrary DOM</p>
          <div className="prose">
            <h2>Ordinary page content</h2>
            <p>
              This column is plain DOM and stays plain DOM. Select this sentence, tab through the
              link, type into a field — nothing here is painted into a canvas, which is what makes
              the glass above it composable with a real application.
            </p>
            <p>
              A dom-backdrop group samples what is behind it through the browser&rsquo;s own{" "}
              <code>backdrop-filter</code>, so the material adapts to whatever the app renders.
            </p>
          </div>
        </section>

        <section className="region region--texture">
          <p className="region__label">backdrop: registered texture</p>
          <TextureBackdrop sourceId={TEXTURE_SOURCE.id} />
        </section>

        <CapabilitiesPanel
          groups={GROUPS}
          overrides={overrides}
          onOverridesChange={setOverrides}
          variantMixed={variantMixed}
          onVariantMixedChange={setVariantMixed}
        />

        <p className="visually-hidden" role="status">
          {lastAction === null ? "" : `Last action: ${lastAction}`}
        </p>
      </main>

      {/*
        The glass: one grid mirroring the page's, inside the base plane.

        Landmark roles are on these containers, not on the page's `<main>`,
        because X1 puts glass in vitrea's own plane DOM — outside every landmark
        the app wrote. An app that portals content into a plane owns giving it a
        place in the document's structure; nothing else can.
      */}
      <PlanePortal plane="base">
        <div className="overlay-grid" role="region" aria-label="Glass surfaces">
          <div className="overlay-cell">
            <GlassGroup id="dom-region" hint={{ tone: "dark", luminance: 0.18 }}>
              <GlassSurface className="plate" radius={22} thickness={10} data-testid="dom-plate">
                <strong>Regular material</strong>
                <span>dom backdrop · author hint</span>
              </GlassSurface>
            </GlassGroup>
          </div>

          <div className="overlay-cell">
            <GlassGroup
              id="texture-region"
              backdrop={TEXTURE_SOURCE}
              dimming={DEFAULT_CLEAR_DIMMING}
            >
              <div className="plate-pair">
                <GlassSurface
                  className="plate"
                  radius={22}
                  thickness={14}
                  data-testid="texture-plate"
                >
                  <strong>Larger surface</strong>
                  <span>deeper material, stronger lensing</span>
                </GlassSurface>
                <GlassSurface
                  className="plate plate--small"
                  radius={14}
                  thickness={6}
                  variant={variantMixed ? "clear" : "regular"}
                  data-testid="texture-plate-small"
                >
                  <span>{variantMixed ? "clear" : "regular"}</span>
                </GlassSurface>
              </div>
            </GlassGroup>
          </div>

          <div />
        </div>
      </PlanePortal>

      <PlanePortal plane="base">
        <div className="segmented-wrap" role="region" aria-label="View controls">
          <GlassGroup id="segmented">
            <GlassSegmentedControl
              aria-label="Time range"
              className="segmented"
              segmentClassName="segment"
              indicatorClassName="segment-indicator"
              items={RANGES}
              value={range}
              onChange={setRange}
            />
          </GlassGroup>
        </div>
      </PlanePortal>

      <PlanePortal plane="base">
        <nav className="toolbar-region" aria-label="Playground toolbar">
      <GlassToolbar
        aria-label="Playground actions"
        className="toolbar"
        groupProps={{ id: "toolbar" }}
      >
        <GlassButton className="control" onClick={() => setLastAction("share")}>
          Share
        </GlassButton>
        <GlassIconButton
          aria-label={favorite ? "Remove from favorites" : "Add to favorites"}
          aria-pressed={favorite}
          className="control control--icon"
          onClick={() => setFavorite((current) => !current)}
        >
          <span aria-hidden="true">{favorite ? "★" : "☆"}</span>
        </GlassIconButton>
        <GlassButton className="control" disabled>
          Disabled
        </GlassButton>
        {/*
          The morph gets a sampling group of its own, and a gap wide enough that
          the two groups' padded proxies do not meet.

          Both are forced by the same thing: `GlassMorph` leaves its closed platter
          in the plane host layer's own flow until it has measured itself, so for a
          frame or two there is a registered box at the plane's origin. Inside the
          toolbar's group that transient stretches the group's proxy union across
          the whole viewport, and every other group on the plane then reports an
          overlap that its settled layout does not have. See `DESIGN.md` §9; this
          was the source of Decision Log #24's demo-diagnostics item.
        */}
        <div className="toolbar__menu">
          <GlassGroup id="toolbar-menu">
            <ActionsMenu onAction={setLastAction} />
          </GlassGroup>
        </div>
      </GlassToolbar>
        </nav>
      </PlanePortal>
    </GlassRoot>
  );
}
