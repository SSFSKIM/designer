/**
 * The instrument window: the one place on this site where glass exists.
 *
 * The stage is `position: fixed` and the narrative column beside it is what
 * scrolls. That split is not a layout preference, it is X1: glass lives in
 * viewport-fixed planes, arbitrary interleaving with foreign stacking contexts is
 * out of contract for v1, and a page that scrolled its own glass out from under
 * itself would be this library lying on its own home page.
 *
 * ## Why there are two trees for one picture
 *
 * X1's paint order puts the semantic host DOM *between* the optics canvas and the
 * highlight canvas, so every glass host has to live inside its plane's host layer,
 * which is vitrea's DOM and not the app's. The page therefore writes the stage
 * twice: `StageGround` is the ordinary DOM behind the glass (the texture canvas,
 * the fixture rasters, the captions), and `StageGlass` is the same geometry
 * rendered inside the plane. Both are given the identical fixed box and the
 * identical layout rules, so they line up by construction rather than by
 * measurement.
 *
 * ## Placement law (`DESIGN.md` §9)
 *
 * Every stack here is top-and-left aligned with a fixed inset, never centred, and
 * the morph is always last. A centred stack re-centres when the morph's anchor
 * spacer grows from zero to its measured size on the second frame, which moves
 * hosts that are already registered and lets core compare two bounds measured in
 * different epochs. Gaps between separate sampling groups are 4rem, comfortably
 * past the 48px that two 24px `samplingPadding` defaults require.
 */

import {
  GlassButton,
  GlassGroup,
  GlassIconButton,
  GlassSegmentedControl,
  GlassSurface,
  GlassToolbar,
} from "vitrea-react";
import { useState, type ReactNode } from "react";

import { ActionsMenu } from "../ActionsMenu";
import { REPORTS_BY_SCENE } from "./calibration";
import { StageBackdrop } from "./StageBackdrop";
import { CANVAS, type ReferenceScene } from "./scenes";

export type StageMode = "material" | "reference" | "behavior" | "access";

export const TEXTURE_SOURCE_ID = "vitrea.site.stage";
export const RASTER_SOURCE_ID = "vitrea.site.raster";

/** The groups each mode puts on the base plane, for the runtime readout. */
export const GROUPS_BY_MODE: Record<StageMode, readonly { id: string; label: string }[]> = {
  material: [{ id: "material", label: "material (registered texture)" }],
  reference: [{ id: "reference", label: "reference (fixture raster as texture)" }],
  behavior: [
    { id: "behavior-bar", label: "behavior-bar (arbitrary DOM)" },
    { id: "behavior-range", label: "behavior-range (arbitrary DOM)" },
    { id: "behavior-menu", label: "behavior-menu (arbitrary DOM)" },
  ],
  access: [{ id: "access", label: "access (registered texture)" }],
};

/**
 * X6's hint, and it is load-bearing rather than decorative.
 *
 * Without it a group with `analysis: none` takes its foreground from explicit
 * tokens or `color-scheme`, and this document's `color-scheme` is `light` — so a
 * control sitting on glass over the *dark* instrument window was being given dark
 * ink on a dark surface, measured at 1.6:1 to 3.0:1. The hint is the one mechanism
 * for telling the runtime what it cannot see (§honesty core), and this is exactly
 * what it is for. It is deliberately absent on the `reference` group: that cell is
 * a fidelity comparison against a capture over a light raster, and biasing its
 * foreground by hand is the one place a hint would be a thumb on the scale.
 */
const STAGE_HINT = { tone: "dark", luminance: 0.16 } as const;

const RANGES = [
  { value: "day", label: "Day" },
  { value: "week", label: "Week" },
  { value: "month", label: "Month" },
] as const;

type Range = (typeof RANGES)[number]["value"];

export type ReferencePanel = "live" | "native";

export interface StageProps {
  readonly mode: StageMode;
  readonly scene: ReferenceScene;
  /**
   * Which half of the pair the collapsed layout shows. Two 320px panels do not fit
   * side by side on a phone, and scaling them both down far enough to fit makes a
   * fidelity comparison unreadable, so the narrow layout shows one at a time and
   * the wide layout ignores this entirely (`site.css` decides which applies).
   */
  readonly panel: ReferencePanel;
  readonly onPanelChange: (next: ReferencePanel) => void;
  readonly animate: boolean;
  readonly lastAction: string | null;
  readonly onAction: (key: string) => void;
  readonly onRasterLoad: (image: HTMLImageElement) => void;
}

/* ── The ordinary DOM behind the glass ─────────────────────────────────────── */

export function StageGround(props: StageProps): ReactNode {
  const { mode, scene } = props;
  const reports = REPORTS_BY_SCENE.get(scene.id) ?? [];
  const report = reports[0];

  return (
    <div
      className="stage"
      data-mode={mode}
      role="region"
      aria-label={mode === "reference" ? "Reference captures" : "Material window"}
    >
      {mode === "reference" ? (
        <div className="stage__inner">
          <div className="pair" data-panel={props.panel}>
            <figure className="pair__cell" data-cell="live">
              <img
                className="pair__raster"
                src={scene.backgroundFile}
                width={CANVAS.width}
                height={CANVAS.height}
                alt=""
                onLoad={(event) => props.onRasterLoad(event.currentTarget)}
              />
              <figcaption className="pair__caption">
                <span className="pair__who">vitrea, live in this browser</span>
                <span className="pair__what">
                  {scene.component} on {scene.background}
                </span>
              </figcaption>
            </figure>
            <figure className="pair__cell" data-cell="native">
              <img
                className="pair__raster"
                src={scene.nativeCapture}
                width={CANVAS.width}
                height={CANVAS.height}
                alt={`Screen capture of Apple's own Liquid Glass rendering the ${scene.component} scene on the ${scene.background} background, macOS 26.5.`}
              />
              <figcaption className="pair__caption">
                <span className="pair__who">macOS 26.5, captured</span>
                <span className="pair__what">ScreenCaptureKit, 1x, sRGB</span>
              </figcaption>
            </figure>
          </div>

          {/* Only ever operable in the collapsed layout; `site.css` hides it above
              the breakpoint, where both panels are on screen at once. */}
          <fieldset className="panel-switch">
            <legend>Panel</legend>
            {(["live", "native"] as const).map((value) => (
              <label key={value}>
                <input
                  type="radio"
                  name="reference-panel"
                  value={value}
                  checked={props.panel === value}
                  onChange={() => props.onPanelChange(value)}
                />
                {value === "live" ? "vitrea, live" : "macOS 26.5"}
              </label>
            ))}
          </fieldset>

          {report === undefined ? (
            <p className="note note--slot">
              No measured cell for this scene yet. Every figure on this page is read
              from the result matrix and keyed to the cell that produced it, so a
              scene without one shows this rather than a number borrowed from a
              different cell. Reference-calibrated; see the calibration report.
            </p>
          ) : (
            <dl className="readout readout--figures">
              {report.figures.map((figure) => (
                <div className="readout__row" key={figure.label}>
                  <dt>{figure.label}</dt>
                  <dd>
                    {figure.value}
                    {figure.unit === "" ? "" : ` ${figure.unit}`}
                  </dd>
                </div>
              ))}
              <div className="readout__row readout__row--cell">
                <dt>Cell</dt>
                <dd>
                  {report.profileKey} × {report.engine} {report.engineVersion},{" "}
                  {report.renderer}, {report.samplingBackend}, {report.gpuAdapter}
                  {", "}
                  {report.tier} tier, {report.fixtureSet} set
                </dd>
              </div>
            </dl>
          )}
        </div>
      ) : (
        <>
          <StageBackdrop sourceId={TEXTURE_SOURCE_ID} animate={props.animate} />
          <p className="stage__legend">
            {mode === "material"
              ? "One sampling group, two surfaces. The larger plate carries more material thickness, so it lenses harder over the same backdrop."
              : mode === "behavior"
                ? "Three sampling groups over arbitrary DOM. Press any control, slide the range, open the menu."
                : "One surface, under whatever the accessibility controls beside it resolve to."}
          </p>
          <p className="visually-hidden" role="status">
            {props.lastAction === null ? "" : `Last action: ${props.lastAction}`}
          </p>
        </>
      )}
    </div>
  );
}

/* ── The same geometry, inside the plane ───────────────────────────────────── */

export function StageGlass(props: StageProps): ReactNode {
  const { mode, scene } = props;
  const [range, setRange] = useState<Range>("week");
  const [favorite, setFavorite] = useState(false);

  if (mode === "reference") {
    return (
      <div className="stage stage--mirror" data-mode={mode} role="region" aria-label="Live vitrea render">
        <div className="stage__inner">
          <div className="pair" data-panel={props.panel}>
            <div className="pair__cell pair__cell--mirror" data-cell="live">
              <div className="pair__raster pair__raster--mirror">
                <GlassGroup id="reference" backdrop={{ kind: "texture", id: RASTER_SOURCE_ID }}>
                  <GlassSurface
                    className="scene-surface"
                    profile="continuous"
                    capsule={scene.box.capsule}
                    radius={scene.box.radius}
                    thickness={8}
                    /*
                     * Percentages of the canvas, not pixels. The raster is 320x200
                     * at full size and scales down at the collapsed breakpoint, and
                     * the surface has to scale with it or the pair stops being a
                     * comparison. At full size these resolve to exactly the
                     * integers `scenes.json` implies, which is what the suite
                     * asserts.
                     */
                    style={{
                      left: `${(scene.box.left / CANVAS.width) * 100}%`,
                      top: `${(scene.box.top / CANVAS.height) * 100}%`,
                      width: `${(scene.box.width / CANVAS.width) * 100}%`,
                      height: `${(scene.box.height / CANVAS.height) * 100}%`,
                    }}
                    data-testid="scene-surface"
                  />
                </GlassGroup>
              </div>
            </div>
            {/* Holds the native cell's place so the pair lays out identically here. */}
            <div className="pair__cell pair__cell--mirror" data-cell="native" aria-hidden="true">
              <div className="pair__raster pair__raster--mirror" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className="stage stage--mirror"
      data-mode={mode}
      role="region"
      aria-label={mode === "behavior" ? "Live vitrea controls" : "Live vitrea surfaces"}
    >
      <div className="stage__stack">
        {mode === "material" ? (
          <GlassGroup id="material" backdrop={{ kind: "texture", id: TEXTURE_SOURCE_ID }} hint={STAGE_HINT}>
            {/*
              One short line each, and nothing else. `DESIGN.md` §8: prose does not
              go on glass, because a material never carries information and because
              small text over a translucent surface on a moving backdrop cannot be
              held to a contrast ratio. What these plates mean is in the column.
            */}
            <GlassSurface className="plate plate--lg" radius={26} thickness={18}>
              <strong>18px thick</strong>
            </GlassSurface>
            <GlassSurface className="plate plate--sm" radius={14} thickness={5}>
              <strong>5px</strong>
            </GlassSurface>
          </GlassGroup>
        ) : null}

        {mode === "access" ? (
          <GlassGroup id="access" backdrop={{ kind: "texture", id: TEXTURE_SOURCE_ID }} hint={STAGE_HINT}>
            <GlassSurface className="plate plate--lg" radius={26} thickness={16}>
              <strong>Regular material</strong>
            </GlassSurface>
          </GlassGroup>
        ) : null}

        {mode === "behavior" ? (
          <>
            <GlassToolbar
              aria-label="Document actions"
              className="bar"
              groupProps={{ id: "behavior-bar", hint: STAGE_HINT }}
            >
              <GlassButton className="control" onClick={() => props.onAction("share")}>
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
              {/*
                The label is wrapped because the *host's* `color` is the runtime's:
                platform-web writes it inline every frame, so an app rule on the
                host loses to it. Restyling a glass host's ink therefore has to
                happen on a child, and `site.css` says what the wrapper is for.
              */}
              <GlassButton className="control" disabled>
                <span className="control__label">Publish</span>
              </GlassButton>
            </GlassToolbar>

            <GlassGroup id="behavior-range" hint={STAGE_HINT}>
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

            {/*
              Last in the stack, and in a group of its own. Both are §9's law: the
              closed platter is measured before it pins, and until it pins it is a
              registered box at the plane layer's origin.
            */}
            <GlassGroup id="behavior-menu" hint={STAGE_HINT}>
              <ActionsMenu label="Document actions" onAction={props.onAction} />
            </GlassGroup>
          </>
        ) : null}
      </div>
    </div>
  );
}
