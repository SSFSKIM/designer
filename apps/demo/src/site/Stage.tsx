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
} from "@vitreajs/vitrea-react";
import { useState, type ReactNode } from "react";

import { ActionsMenu } from "../ActionsMenu";
import { REPORTS_BY_SCENE } from "./calibration";
import { DEFAULT_GROUND, StageBackdrop, type StageGroundPaint } from "./StageBackdrop";
import { CANVAS, type ReferenceScene } from "./scenes";

export type StageMode = "material" | "tone" | "reference" | "behavior" | "access";

export const TEXTURE_SOURCE_ID = "vitrea.site.stage";
export const RASTER_SOURCE_ID = "vitrea.site.raster";

/** The groups each mode puts on the base plane, for the runtime readout. */
export const GROUPS_BY_MODE: Record<StageMode, readonly { id: string; label: string }[]> = {
  material: [{ id: "material", label: "material (registered texture)" }],
  tone: [{ id: "tone", label: "tone (registered texture, declared level)" }],
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

/**
 * The size sweep's steps — the material stage's controlled comparison (W2).
 *
 * One authored thickness for all three, declared once here rather than three
 * times at the call sites, because it is the sweep's **control**: if the plates
 * ever stopped agreeing on it the stage would look the same and would have
 * stopped demonstrating the size law. `spanPx` is each plate's short side, and
 * `site.css` is where the boxes are actually sized — these numbers are the label
 * and the e2e's expectation, and the CSS carries the same three.
 *
 * The three straddle the shipped profile's own band (32…96 px): the first sits at
 * the law's floor, the last past its ceiling, the middle one mid-curve.
 *
 * The sweep also carries the author tint's demonstration (W3), on its largest
 * plate. The two features share this stage rather than taking turns on it because
 * sharing it is the better demonstration of both: the tint control changes what
 * the material's tint layer is made of and leaves `--vitrea-occlusion` exactly
 * where it was, while the plate it sits on goes on reading thicker than its two
 * neighbours. A tinted platter is still a platter. `testId` is what the tint's own
 * e2e reads, and it needs one tinted plate and one plain one to compare.
 */
const SWEEP_THICKNESS = 8;

const SIZE_SWEEP = [
  { step: "c", spanPx: 112, radius: 26, tinted: true, testId: "tinted-plate" },
  { step: "b", spanPx: 68, radius: 18, tinted: false, testId: undefined },
  { step: "a", spanPx: 40, radius: 12, tinted: false, testId: "untinted-plate" },
] as const;

/**
 * The backdrop tone stage's ground control (W7).
 *
 * The reader drives ONE number: the linear luminance of the flat ground the
 * instrument window is painted in, which is also the level this stage's group
 * declares as its backdrop hint. The two are the same number by construction —
 * the page paints that ground, so it is not estimating anything when it says what
 * it is.
 *
 * The stops are the axis's own, not a comfortable range around it. Below the
 * curve's `backdropToneLow` (0.02 linear) a small surface is fully adapted; above
 * its `backdropToneHigh` (0.14) nothing adapts at all, whatever its size. `max` is
 * `STAGE_HINT`'s own 0.16 rather than a round number, because that is the answer to
 * the question this stage raises: the rest of the page declares 0.16, 0.16 is past
 * the band, and that is the entire reason the other stages look untouched by this
 * feature. Sliding to the top reproduces them.
 *
 * `initial` is mid-band on purpose. It is the one setting at which the three
 * plates are all visibly *different* from each other, so the stage opens on the
 * size gate rather than on either of its ends.
 *
 * They are counted in integer THOUSANDTHS, and that is not a formatting choice. A range
 * input validates its value against `min + n * step` in binary floating point, and
 * a 0.002 grid does not land on the decimals it is written with — `0.002 * 5` is
 * not `0.01` — so a fractional slider rejects most of its own positions the moment
 * anything sets one by value. The reader sees the quantity itself either way: the
 * field prints it, and `aria-valuetext` announces it.
 */
export const TONE_GROUND = {
  min: 2,
  max: 160,
  step: 2,
  initial: 30,
  /** Thousandths back to the linear luminance the material is a function of. */
  level: (thousandths: number): number => thousandths / 1000,
} as const;

/**
 * The ground colour for a declared linear level — the sRGB transfer function, and
 * grey rather than the window's hue.
 *
 * Achromatic because the hint this stage declares carries a level and not a
 * colour, so the material adapts onto a grey; a ground with hue in it would leave
 * the adapted plate a visibly different colour from the backdrop it is supposed to
 * have joined, and the page would be demonstrating the hint's one documented
 * coarseness rather than the axis.
 */
function groundFill(level: number): string {
  const clamped = Math.min(1, Math.max(0, level));
  const encoded = clamped <= 0.0031308 ? clamped * 12.92 : 1.055 * clamped ** (1 / 2.4) - 0.055;
  const channel = Math.round(encoded * 255);
  return `rgb(${channel} ${channel} ${channel})`;
}

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
  /**
   * The author tint on the thick plate — a CSS colour, or `null` for none.
   *
   * Only the thick plate takes it, deliberately. Apple's guidance is to colour
   * one control for emphasis rather than a whole container, and one tinted
   * surface beside an untinted one in the same group is also the composition
   * worth showing: tint strength is a per-pixel quantity, so the two plates come
   * out of a single optics pass wearing different colours.
   */
  readonly tint: string | null;
  /**
   * The tone stage's backdrop level, linear 0..1 — what the reader is driving.
   *
   * It reaches the material twice over, and both are the same statement: it is the
   * ground the canvas is painted in, and it is the `luminance` this stage's group
   * declares. Ignored by every other mode, whose ground is the window's own.
   */
  readonly groundLevel: number;
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
  const ground: StageGroundPaint =
    mode === "tone" ? { fill: groundFill(props.groundLevel), field: 0 } : DEFAULT_GROUND;

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
          <StageBackdrop sourceId={TEXTURE_SOURCE_ID} animate={props.animate} ground={ground} />
          {/*
            No caption on the tone stage, and it is the same rule that keeps prose
            off the glass: this is the one ground on the page whose lightness the
            reader is driving, and no single ink can be held to a contrast ratio
            across the whole sweep — at the top stop the dim stage ink measures
            2.4:1 against the ground it is sitting on. What that stage means is in
            the column, beside the control that moves it.
          */}
          {mode === "tone" ? null : (
            <p className="stage__legend">
              {mode === "material"
                ? "One sampling group, three surfaces, one authored thickness. Only the size differs — and the larger a surface gets, the harder it lenses and the deeper it sits."
                : mode === "behavior"
                  ? "Three sampling groups over arbitrary DOM. Press any control, slide the range, open the menu."
                  : "One surface, under whatever the accessibility controls beside it resolve to."}
            </p>
          )}
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
              The size law, as a controlled comparison (W2). Every plate declares
              the SAME authored thickness, so the only thing that differs between
              them is how big they are — which is the whole claim: Apple's material
              "simulates a thicker, more substantial material" as it grows, and
              nothing here is telling it to.

              Three steps rather than two, because the law is a curve with a floor
              and a ceiling and two points cannot show a curve. The plates' short
              spans (40, 68 and 112 px) straddle the profile's own band: the first
              is at the law's zero, the last is past its saturation, and the middle
              one is genuinely mid-curve. They are also one sampling group over one
              registered texture, so the comparison is over identical backdrop
              pixels rather than over three separate samplings of a moving one.

              One short line each, and nothing else. `DESIGN.md` §8: prose does not
              go on glass, because a material never carries information and because
              small text over a translucent surface on a moving backdrop cannot be
              held to a contrast ratio. What these plates mean is in the column.
            */}
            {SIZE_SWEEP.map((step) => (
              <GlassSurface
                key={step.step}
                className={`plate plate--sweep plate--sweep-${step.step}`}
                radius={step.radius}
                thickness={SWEEP_THICKNESS}
                data-sweep-thickness={SWEEP_THICKNESS}
                data-testid={step.testId}
                {...(step.tinted ? { tint: props.tint } : {})}
              >
                <strong>
                  {step.spanPx}px{step.tinted && props.tint !== null ? ", tinted" : ""}
                </strong>
              </GlassSurface>
            ))}
          </GlassGroup>
        ) : null}

        {mode === "tone" ? (
          /*
           * Backdrop tone adaptation (W7), as the same controlled comparison the
           * size sweep already is.
           *
           * The plates are literally `SIZE_SWEEP` — the same three short spans,
           * the same one authored thickness — because the two stages are one
           * story: the size law says a bigger surface reads thicker, and this axis
           * is gated by that same thickness, so a surface that already looked more
           * substantial also holds its own appearance longer over a dark backdrop.
           * Re-deriving a second set of spans here would let the two drift and
           * would break the reader's ability to carry the first stage into this
           * one. `tinted` and `testId` belong to the sweep's other claim (W3) and
           * are not read here; this stage tints nothing, because a declared colour
           * is step three of the composition contract and would confound step two.
           *
           * The group declares its backdrop level rather than leaving it to be
           * measured, and that is not a shortcut. X6's rule is that a stated fact
           * beats a reading, this page paints the ground it is standing on, and —
           * the part that is not optional — the runtime's foreground decision only
           * has a backdrop to reason about when a group declares one. Without the
           * hint the material would still adapt and the ink would still be chosen
           * against a backdrop nobody described, which on a fully adapted 40px
           * plate is the wrong ink on a surface that has just gone dark.
           */
          <GlassGroup
            id="tone"
            backdrop={{ kind: "texture", id: TEXTURE_SOURCE_ID }}
            hint={{ tone: "dark", luminance: props.groundLevel }}
          >
            {SIZE_SWEEP.map((step) => (
              <GlassSurface
                key={step.step}
                className={`plate plate--sweep plate--sweep-${step.step}`}
                radius={step.radius}
                thickness={SWEEP_THICKNESS}
                data-testid={`tone-plate-${step.step}`}
              >
                <strong>{step.spanPx}px</strong>
              </GlassSurface>
            ))}
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
