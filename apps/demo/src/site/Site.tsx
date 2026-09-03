/**
 * vitrea's public demo site.
 *
 * Composed under `apps/demo/DESIGN.md` (stance: survey plate). The page is a
 * measurement document with an instrument set into it: the narrative scrolls in
 * the left column, and the right column is a fixed stage where the material is
 * actually running. Everything visual lives in `site.css` and `tokens.css`; this
 * file carries structure, content and state.
 *
 * The internal acceptance playground still exists, unchanged, at `/playground/`.
 * It is what C8's Playwright suite drives and it is deliberately outside this
 * page's design law.
 */

import {
  PlanePortal,
  useGlassAccessibility,
  useGlassRoot,
  type AccessibilityOverride,
} from "@vitreajs/vitrea-react";
import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";

import { MEASURED_CELL_COUNT } from "./calibration";
import { DiagnosticsReadout, GroupReadout } from "./Readout";
import { REFERENCE_SCENES, NATIVE_PROFILE, type ReferenceScene } from "./scenes";
import {
  GROUPS_BY_MODE,
  RASTER_SOURCE_ID,
  StageGlass,
  StageGround,
  TONE_GROUND,
  type ReferencePanel,
  type StageMode,
} from "./Stage";

export interface Overrides {
  readonly reducedMotion: AccessibilityOverride;
  readonly reducedTransparency: AccessibilityOverride;
  readonly increasedContrast: AccessibilityOverride;
}

export interface SiteProps {
  readonly requestedRenderer: "css" | "webgpu";
  /** Owned above, because these are `GlassRoot` construction props. */
  readonly overrides: Overrides;
  readonly onOverridesChange: (next: Overrides) => void;
}

interface SectionSpec {
  readonly id: string;
  readonly title: string;
  readonly mode: StageMode;
}

const SECTIONS: readonly SectionSpec[] = [
  { id: "material", title: "The material", mode: "material" },
  { id: "tone", title: "Taking the tone of the backdrop", mode: "tone" },
  { id: "reference", title: "Measured against the real thing", mode: "reference" },
  { id: "behavior", title: "Behaviour", mode: "behavior" },
  { id: "access", title: "Accessibility is a resolved state", mode: "access" },
  { id: "tiers", title: "What each browser actually gets", mode: "material" },
  { id: "install", title: "Install", mode: "material" },
];

/** The one cell that has actually been measured, so the pair opens on a figure. */
const DEFAULT_SCENE: ReferenceScene = (() => {
  const found =
    REFERENCE_SCENES.find((scene) => scene.id === "checkerboard__capsule-button__rest") ??
    REFERENCE_SCENES[0];
  if (found === undefined) throw new Error("scenes.json declares no displayable scene.");
  return found;
})();

/**
 * The tint control's options.
 *
 * A `<select>` rather than a colour picker, and a short list rather than a
 * spectrum: the point on the page is that a tint is a *seed read through a tone
 * map*, which reads across a few well-separated hues and a half-strength case
 * far better than it does across a continuum nobody stops on. The half-strength
 * entry carries its alpha in the colour, which is how the API takes it.
 */
const TINT_OPTIONS = [
  { label: "none", name: "None", value: null },
  { label: "orange", name: "Orange", value: "#ff9500" },
  { label: "blue", name: "Blue", value: "#0a84ff" },
  { label: "green", name: "Green", value: "#30d158" },
  { label: "orange-half", name: "Orange, half strength", value: "rgb(255 149 0 / 50%)" },
] as const;

const OVERRIDE_FIELDS = [
  ["reducedMotion", "Reduced motion"],
  ["reducedTransparency", "Reduced transparency"],
  ["increasedContrast", "Increased contrast"],
] as const;

/**
 * Which section the reader is on, and therefore which mode the stage shows.
 *
 * A band across the middle of the viewport rather than a scroll position: the
 * section that crosses the reader's own line of sight is the one the instrument
 * should be demonstrating. `rootMargin` shrinks the observation root to that band,
 * so exactly one section is intersecting at a time except at the boundaries, where
 * the later one wins.
 */
function useActiveSection(): string {
  const [active, setActive] = useState<string>(SECTIONS[0]?.id ?? "material");

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const hit = entries.filter((entry) => entry.isIntersecting).at(-1);
        if (hit !== undefined) setActive(hit.target.id);
      },
      { rootMargin: "-45% 0px -45% 0px", threshold: 0 },
    );
    for (const section of SECTIONS) {
      const element = document.getElementById(section.id);
      if (element !== null) observer.observe(element);
    }
    return () => observer.disconnect();
  }, []);

  return active;
}

export function Site(props: SiteProps): ReactNode {
  const root = useGlassRoot();
  const policy = useGlassAccessibility();
  const active = useActiveSection();
  const [scene, setScene] = useState<ReferenceScene>(DEFAULT_SCENE);
  const [lastAction, setLastAction] = useState<string | null>(null);
  const [panel, setPanel] = useState<ReferencePanel>("live");
  const [tintOption, setTintOption] = useState<string>("none");
  const tint = TINT_OPTIONS.find((entry) => entry.label === tintOption)?.value ?? null;
  /*
   * The tone stage's one variable, held in the slider's own integer thousandths
   * and converted where it is used. The state is the control's value rather than
   * the physical quantity so that nothing has to round back into the step grid.
   */
  const [groundStep, setGroundStep] = useState<number>(TONE_GROUND.initial);
  const groundLevel = TONE_GROUND.level(groundStep);
  const { overrides, onOverridesChange } = props;

  const mode = useMemo<StageMode>(
    () => SECTIONS.find((section) => section.id === active)?.mode ?? "material",
    [active],
  );

  /*
   * The fixture raster, handed to the renderer as the reference cell's texture.
   *
   * `GlassGroup`'s `backdrop` prop declares the source; this hands over the pixels,
   * which core cannot hold (X4) — and handing them over is the whole wiring, since
   * `setBackdropTexture` marks the source dirty itself. Registering the very
   * raster the native harness composited over is what makes the pair a comparison
   * rather than an illustration: both sides sample the same bytes.
   */
  const rasterRef = useRef<HTMLImageElement | null>(null);
  useEffect(() => {
    const image = rasterRef.current;
    if (root === null || image === null) return;
    root.setBackdropTexture(RASTER_SOURCE_ID, { kind: "image", image });
  }, [root, scene]);

  const stageProps = {
    mode,
    scene,
    panel,
    onPanelChange: setPanel,
    tint,
    groundLevel,
    animate: policy?.reducedMotion !== true,
    lastAction,
    onAction: setLastAction,
    onRasterLoad: (image: HTMLImageElement) => {
      rasterRef.current = image;
      if (root === null) return;
      root.setBackdropTexture(RASTER_SOURCE_ID, { kind: "image", image });
    },
  } as const;


  return (
    <>
      <StageGround {...stageProps} />

      <main className="column">
        <header className="masthead">
          <p className="wordmark">vitrea</p>
          <h1 className="display">Liquid Glass, for the web</h1>
          <p className="lead">
            A material compositor for semantic web controls: explicit backdrop
            contracts, shared sampling groups, coherent morphing, and fidelity
            claims backed by captures of Apple&rsquo;s own renderer.
          </p>
          <p className="body">
            The window on the right is running the real thing in this browser, on
            whatever tier this browser can actually give it. Scroll, and it follows
            what you are reading.
          </p>
          <nav className="jump" aria-label="Sections">
            <ul>
              {SECTIONS.map((section) => (
                <li key={section.id}>
                  <a href={`#${section.id}`} aria-current={active === section.id ? "true" : undefined}>
                    {section.title}
                  </a>
                </li>
              ))}
            </ul>
          </nav>
        </header>

        <Section spec={SECTIONS[0]} active={active}>
          <p className="body">
            Liquid Glass is not a blur preset. It is size-parameterised lensing,
            per-element adaptation of tint and foreground to whatever is actually
            behind the surface, and sampling that is scoped to a container rather
            than to a single element. No CSS filter chain expresses that, which is
            why the optics run on the GPU.
          </p>
          <p className="body">
            All three plates in the window belong to one sampling group over one
            registered texture, and all three are authored at the same 8px material
            thickness. The only thing that differs is how big they are — their short
            sides are 40, 68 and 112 px. Watch the edges: the largest plate bends the
            backdrop further and sits on a deeper shadow than the smallest, and
            nothing on this page asked it to.
          </p>
          <p className="body">
            That is the size law, and it is measured rather than styled. Apple&rsquo;s
            material &ldquo;simulates a thicker, more substantial material&rdquo; as
            it grows, and the settled macOS 26.5 reference does exactly that: over
            one fixed backdrop it passes 0.244 of that backdrop&rsquo;s contrast at a
            32px span, 0.230 at 44px and 0.144 at 96px. vitrea&rsquo;s band is fitted
            to where that movement happens, so a control at 40px sits at the
            law&rsquo;s floor and a platter past 96px at its ceiling.
          </p>
          <Fields legend="Renderer">
            <RendererField requested={props.requestedRenderer} />
          </Fields>
          <Fields legend="Tint">
            <label className="field">
              <span className="field__label">Tint</span>
              <select
                value={tintOption}
                onChange={(event) => setTintOption(event.target.value)}
                data-testid="tint-select"
              >
                {TINT_OPTIONS.map((entry) => (
                  <option key={entry.label} value={entry.label}>
                    {entry.name}
                  </option>
                ))}
              </select>
            </label>
          </Fields>
          <p className="body">
            The tint is a seed, not a fill. Apple&rsquo;s material maps a chosen
            colour to a range of tones against the brightness behind it, and a solid
            fill is the failure the same session names &mdash; &ldquo;completely
            opaque, and breaks the visual character of Liquid Glass&rdquo;. So the
            colour here becomes a shade of itself &mdash; darker over dark content,
            the seed over light &mdash; at the strength the colour&rsquo;s own alpha
            carries: at full strength the shade is opaque, as the reference&rsquo;s
            is, and at half strength the material still shows through it. What
            never moves is the material&rsquo;s own opacity, the value Reduce
            Transparency and Increase Contrast operate on, so both plates keep their
            calibrated material under any tint. The colour lands on one plate
            rather than the group, which is also the guidance &mdash; colour one
            control for emphasis, not every control.
          </p>
          {GROUPS_BY_MODE.material.map((group) => (
            <GroupReadout key={group.id} id={group.id} label={group.label} />
          ))}
          <DiagnosticsReadout />
        </Section>

        <Section spec={SECTIONS[1]} active={active}>
          <p className="body">
            Liquid Glass does not always sit in front of what is behind it. Over a
            dark enough backdrop it takes that backdrop&rsquo;s tone and settles
            into it, and the settled macOS 26.5 reference is unambiguous about how
            far that goes: a 44px capsule over a near-black backdrop comes out
            byte-identical to its own background, while a 96px surface over the
            same backdrop keeps about three quarters of its own appearance. So it
            is one axis with two inputs &mdash; how dark the backdrop is, and how
            big the surface is.
          </p>
          <Fields legend="Backdrop">
            <label className="field">
              <span className="field__label">Ground level</span>
              <input
                className="field__range"
                type="range"
                min={TONE_GROUND.min}
                max={TONE_GROUND.max}
                step={TONE_GROUND.step}
                value={groundStep}
                onChange={(event) => setGroundStep(Number(event.target.value))}
                aria-valuetext={`${groundLevel.toFixed(3)} linear`}
                data-testid="ground-level"
              />
              <span className="field__hint" data-testid="ground-level-readout">
                {groundLevel.toFixed(3)} linear. The curve is flat above 0.14 and
                saturated below 0.02; everything between those two is the
                transition.
              </span>
            </label>
          </Fields>
          <p className="body">
            The window&rsquo;s ground is one flat grey under the graticule while you
            are here, which is the bed this was measured on rather than a plainer
            version of the usual one. A group adapts onto one resolved backdrop
            colour, so a surface only
            joins its backdrop exactly where that backdrop is the same everywhere
            underneath it; over the drifting field above, the same adaptation would
            put a flat average-coloured patch on a graded ground and this page would
            be claiming a convergence while showing an approximation.
          </p>
          <p className="body">
            The three plates are the same three as the sweep above &mdash; 40, 68
            and 112px short spans, one authored thickness of 8px, nothing else
            differing. Drag the ground down and they come apart: the 40px plate
            takes the ground&rsquo;s own colour exactly &mdash; at the bottom stop
            its body and its rim are both the backdrop, and its label is the only
            thing left marking where it is &mdash; while the 68px plate is most of
            the way there and the 112px plate has barely moved. That is the size
            gate, and it is the size law again rather than a second rule. A
            thicker surface reads its backdrop as brighter than it is, so it holds
            its own appearance longer &mdash; the thickness enters the curve&rsquo;s
            argument, not its result.
          </p>
          <p className="body">
            Nothing else on this page does this, and the reason is a number. Every
            other group here declares{" "}
            <code>{'hint={{ tone: "dark", luminance: 0.16 }}'}</code>, because the
            instrument window is dark and the runtime cannot see that for itself
            &mdash; and 0.16 is above the band, so the axis never fires. The
            slider&rsquo;s top stop is that same 0.16: take it there and these
            plates are the plates from the previous section.
          </p>
          <p className="body">
            This group declares its level too, and both halves of that are
            deliberate. A stated fact beats a reading, and this page paints the
            ground it is standing on, so it is not estimating anything. It also has
            to: the runtime picks each plate&rsquo;s ink against the material that
            plate is actually showing, and it can only do that for a group whose
            backdrop was declared. Watch the labels as you drag &mdash; the 40px
            plate&rsquo;s ink turns light as its body goes dark, while the 112px
            plate&rsquo;s stays dark on a body that is still light: one group, two
            answers, in the same frame. An app that cannot state its backdrop still
            gets the adaptation, from the pixels it registered: one average per
            source, re-read when the source says its content changed.
          </p>
          <p className="note">
            Reduced transparency folds this axis down rather than through. That
            preference asked for more occlusion, and a surface dissolving into its
            backdrop is the opposite of it; a material law does not get to outrank a
            policy. Under forced colours there is no material to adapt at all.
          </p>
          {GROUPS_BY_MODE.tone.map((group) => (
            <GroupReadout key={group.id} id={group.id} label={group.label} />
          ))}
        </Section>

        <Section spec={SECTIONS[2]} active={active}>
          <p className="body">
            The left panel is this browser rendering the scene now. The right panel
            is a screen capture of Apple&rsquo;s own <code>glassEffect</code> on
            macOS 26.5, taken through ScreenCaptureKit because Liquid Glass is
            composited by the window server and an application cannot capture its
            own material.
          </p>
          <p className="body">
            Both panels place the same shape at the same coordinates because both
            read the same file. <code>apps/reference-apple/scenes.json</code>{" "}
            declares the canvas, the component sizes and the radii; the SwiftUI
            harness renders from it on macOS and this page renders from it here. The
            backgrounds are the identical pre-rendered rasters, so font
            rasterisation and image decoding never enter the diff.
          </p>
          <Fields legend="Scene">
            <label className="field">
              <span className="field__label">Scene</span>
              <select
                value={scene.id}
                onChange={(event) => {
                  const next = REFERENCE_SCENES.find((entry) => entry.id === event.target.value);
                  if (next !== undefined) setScene(next);
                }}
              >
                {REFERENCE_SCENES.map((entry) => (
                  <option key={entry.id} value={entry.id}>
                    {entry.id} ({entry.fixtureSet})
                  </option>
                ))}
              </select>
            </label>
          </Fields>
          <h3 className="h3">What these numbers are, and are not</h3>
          <ul className="list">
            <li>
              {MEASURED_CELL_COUNT} cell measured so far, against constants that are
              still the seeded advisory defaults. Fidelity tuning is a separate task
              in flight; it writes into the same result matrix this page reads.
            </li>
            <li>
              Every figure is keyed to its cell: native profile, engine and version,
              renderer, sampling backend, GPU adapter class, tier and fixture set.
              The claim is never &ldquo;pixel-identical to Apple&rdquo;. It is
              reference-calibrated against {NATIVE_PROFILE}.
            </li>
            <li>
              1x only. This machine reports a backing scale of 1.0, so the canonical
              2x profiles are unmeasured and are not claimed.
            </li>
            <li>
              The pressed scenes are excluded from this pair on purpose: they compare
              two independently derived poses rather than a measurement against an
              observed one, which makes them a tuning target and not a comparison.
            </li>
            <li>
              The scene split is declared as data, and the holdout ids are named in
              no tuning code. A holdout figure is reported, never fitted to.
            </li>
          </ul>
        </Section>

        <Section spec={SECTIONS[3]} active={active}>
          <p className="body">
            Press any control in the window. Pointer-down produces a glow at the
            press point and about one per cent of compression on a spring; release
            mid-press and the animation redirects from its current position and
            velocity instead of snapping or restarting. Every channel integrates
            closed-form, so 60Hz, 120Hz and a dropped frame produce the same
            response.
          </p>
          <p className="body">
            Open the menu. The button becomes the platter as one continuous material
            transition: geometry, radius and material thickness all interpolate on
            their own springs, and the surface is promoted to the overlay plane as a
            unit so the platter&rsquo;s glass correctly occludes the controls
            underneath it. There is no crossfade of two surfaces, because there is
            only ever one surface.
          </p>
          <p className="body">
            The labels stay real DOM throughout. They are selectable, focusable,
            IME-capable, and announced as the controls they are. Arrow keys move
            within the toolbar and skip the disabled item, because it is a real
            disabled <code>&lt;button&gt;</code> and not a styled div.
          </p>
          {GROUPS_BY_MODE.behavior.map((group) => (
            <GroupReadout key={group.id} id={group.id} label={group.label} />
          ))}
        </Section>

        <Section spec={SECTIONS[4]} active={active}>
          <p className="body">
            Reduced motion removes overshoot, deformation and shimmer travel while
            keeping positional continuity. Reduced transparency frosts the material
            harder, caps refraction and raises occlusion. Increased contrast
            strengthens borders and pushes foregrounds towards monochrome. Each
            follows the system by default and each is overridable, because{" "}
            <code>prefers-reduced-transparency</code> is not Baseline and an
            explicit override is therefore load-bearing rather than a courtesy.
          </p>
          <Fields legend="Accessibility overrides">
            {OVERRIDE_FIELDS.map(([key, label]) => (
              <label className="field" key={key}>
                <span className="field__label">{label}</span>
                <select
                  value={String(overrides[key])}
                  onChange={(event) => {
                    const raw = event.target.value;
                    onOverridesChange({
                      ...overrides,
                      [key]: raw === "system" ? "system" : raw === "true",
                    });
                  }}
                >
                  <option value="system">Follow the system</option>
                  <option value="true">On</option>
                  <option value="false">Off</option>
                </select>
              </label>
            ))}
          </Fields>
          <dl className="readout">
            <div className="readout__head">
              <dt>Resolved policy</dt>
              <dd>read from the runtime</dd>
            </div>
            <div className="readout__row">
              <dt>Glass</dt>
              <dd>{policy?.material.glass ?? "none"}</dd>
            </div>
            <div className="readout__row">
              <dt>Frost</dt>
              <dd>{policy?.material.frost ?? "none"}</dd>
            </div>
            <div className="readout__row">
              <dt>Refraction cap</dt>
              <dd>{policy?.material.refraction ?? "none"}</dd>
            </div>
            <div className="readout__row">
              <dt>Overshoot</dt>
              <dd>{policy?.motion.overshoot ?? "none"}</dd>
            </div>
            <div className="readout__row">
              <dt>Deformation</dt>
              <dd>{policy?.motion.deformation ?? "none"}</dd>
            </div>
            <div className="readout__row">
              <dt>Forced colours</dt>
              <dd>{String(policy?.forcedColors ?? "none")}</dd>
            </div>
          </dl>
          <p className="note">
            Forced colours has no override and never will. It is an operating-system
            mandate, so the type excludes it from the prop set: under it the material
            flattens to system colours and borders, with no glass at all.
          </p>
        </Section>

        <Section spec={SECTIONS[5]} active={active}>
          <p className="body">
            There are two renderers, and the difference between them is stated rather
            than smoothed over.
          </p>
          <h3 className="h3">True refraction</h3>
          <p className="body">
            Where WebGPU is available and the app registers a GPU-ownable backdrop,
            an image, a video, a canvas, a procedural gradient or its own render
            target, the optics run as real lensing. The surface bends the backdrop it
            samples, adaptation comes from luminance, variance and edge-density
            analysis on the GPU, and lensing scales with surface size. That is the
            texture tier: <code>refraction: true</code>,{" "}
            <code>analysis: exact</code>.
          </p>
          <h3 className="h3">Approximation</h3>
          <p className="body">
            Over arbitrary page DOM there is no way to hand the GPU those pixels, so
            the browser&rsquo;s own <code>backdrop-filter</code> does the blur
            through one masked proxy per sampling group, and the GPU draws rim
            lensing, tint, glow and the morph on top. Adaptation comes from an
            author hint or an estimator, and the estimator is always called an
            estimator. That is the dom tier: <code>refraction: approximate</code>,{" "}
            <code>analysis: hint</code> or <code>none</code>.
          </p>
          <h3 className="h3">No refraction</h3>
          <p className="body">
            With no WebGPU, no adapter, or no renderer chunk, every group resolves to
            the CSS tier. It is presentable and it is honest:{" "}
            <code>refraction: none</code>, because <code>backdrop-filter</code>{" "}
            blurs and never bends. Nothing on the page pretends otherwise, and the
            readouts above name the reason.
          </p>
          <h3 className="h3">Choosing is not failing</h3>
          <p className="body">
            A root that never asked for WebGPU resolves to the CSS tier with{" "}
            <code>health: ok</code> and no demotion reason. Labelling intent as a
            fault would invert the whole point of these states. A root that did ask
            and did not get it reports <code>health: demoted</code> with the reason
            named: <code>no-webgpu</code>, <code>no-backdrop-filter</code>,{" "}
            <code>tainted-source</code>, <code>incompatible-texture</code>,{" "}
            <code>device-lost</code>, <code>probe-failed</code> or{" "}
            <code>governor</code>. Each reason carries its own recovery, and{" "}
            <code>no-webgpu</code> honestly carries none within a session.
          </p>
          <h3 className="h3">Per-engine facts, not a support badge</h3>
          <ul className="list">
            <li>
              Chromium: WebGPU on by default since 113 on desktop and 121 on Android.
              Backdrop proxy sampling was measured byte-exact against in-place{" "}
              <code>backdrop-filter</code> across 122 capture variants.
            </li>
            <li>
              Safari 26: WebGPU on by default. Proxy sampling was verified by hand,
              because WebKit renders <code>backdrop-filter</code> as a no-op in every
              automatable capture path while rendering it correctly on screen.
            </li>
            <li>
              Firefox: WebGPU on by default since 141 on Windows and 145 on ARM Macs;
              still behind a flag on Linux. Proxy sampling verified by hand, for the
              same capture-path reason as WebKit.
            </li>
            <li>
              A startup probe checks the proxy topology in the browser actually
              running, and demotes a group to the CSS tier when sampling proves
              non-equivalent. No engine offers a pixel oracle for{" "}
              <code>backdrop-filter</code>, so one failure class stays undetectable
              at runtime and ships as a per-engine conformance table instead of a
              promise.
            </li>
          </ul>
        </Section>

        <Section spec={SECTIONS[6]} active={active}>
          <pre className="code" tabIndex={0}>
            <code>{"npm install @vitreajs/vitrea @vitreajs/vitrea-react"}</code>
          </pre>
          <p className="body">
            Two published packages. The internal geometry, motion and platform layers
            are bundled in, and the WebGPU renderer loads behind a dynamic import, so
            an app that only ever reaches the CSS tier never downloads any WGSL.
          </p>
          <pre className="code" tabIndex={0}>
            <code>{INSTALL_SNIPPET}</code>
          </pre>
          <p className="body">
            That renders glass over ordinary page content through the dom-backdrop
            path, with no setup beyond the root. Register a texture to upgrade a
            group to true refraction:
          </p>
          <pre className="code" tabIndex={0}>
            <code>{TEXTURE_SNIPPET}</code>
          </pre>
          <p className="note">
            One thing an app has to do itself: content portalled into a plane sits
            outside every landmark the page wrote, so give it a{" "}
            <code>&lt;nav&gt;</code> or a named <code>role=&quot;region&quot;</code>.
            Nothing else can, from there.
          </p>
        </Section>

        <footer className="footer">
          <p className="note">
            Apache-2.0. Liquid Glass and macOS are trademarks of Apple Inc.; vitrea
            is an independent implementation and is not affiliated with or endorsed
            by Apple.
          </p>
          <p className="note">
            <a href="laws/">The material laws</a>: one section per measured law,
            each running live with a control and the runtime&rsquo;s own readout.
          </p>
          <p className="note">
            <a href="playground/">Open the internal playground</a>, which is the
            acceptance harness rather than this page.
          </p>
        </footer>
      </main>

      {/*
        One portal for the whole mirror, so the stage's layout survives the move
        into the plane's host layer. Without it every surface would portal for
        itself and the geometry would scatter to the plane root.
      */}
      <PlanePortal plane="base">
        <StageGlass {...stageProps} />
      </PlanePortal>
    </>
  );
}

function Section(props: {
  readonly spec: SectionSpec | undefined;
  readonly active: string;
  readonly children: ReactNode;
}): ReactNode {
  const { spec } = props;
  if (spec === undefined) return null;
  const current = props.active === spec.id;
  return (
    <section
      className="section"
      id={spec.id}
      aria-labelledby={`${spec.id}-title`}
      data-current={current ? "" : undefined}
    >
      {/* Not colour alone: the current section also carries the marker and the
          heading sits at full ink weight while the others do not. */}
      <span className="section__marker" aria-hidden="true" />
      <h2 className="h2" id={`${spec.id}-title`}>
        {spec.title}
      </h2>
      {props.children}
    </section>
  );
}

function Fields(props: { readonly legend: string; readonly children: ReactNode }): ReactNode {
  return (
    <fieldset className="fields">
      <legend className="fields__legend">{props.legend}</legend>
      {props.children}
    </fieldset>
  );
}

/**
 * The renderer is a construction-time choice, so this reloads rather than
 * pretending a root can change tiers in place. Saying so is part of the honesty.
 */
function RendererField(props: { readonly requested: "css" | "webgpu" }): ReactNode {
  return (
    <label className="field">
      <span className="field__label">Requested renderer</span>
      <select
        value={props.requested}
        onChange={(event) => {
          const url = new URL(window.location.href);
          url.searchParams.set("renderer", event.target.value);
          window.location.assign(url.toString());
        }}
      >
        <option value="webgpu">webgpu (ask for the GPU tier)</option>
        <option value="css">css (ask for the CSS tier)</option>
      </select>
      <span className="field__hint">
        Reloads the page: a root wires its renderer once, at construction.
      </span>
    </label>
  );
}

const INSTALL_SNIPPET = `import { GlassRoot, GlassGroup, GlassToolbar, GlassButton } from "@vitreajs/vitrea-react";

export function App() {
  return (
    <GlassRoot renderer="webgpu">
      <YourOrdinaryPage />
      <GlassGroup id="toolbar" hint={{ tone: "dark", luminance: 0.18 }}>
        <GlassToolbar aria-label="Document actions">
          <GlassButton onClick={share}>Share</GlassButton>
        </GlassToolbar>
      </GlassGroup>
    </GlassRoot>
  );
}`;

const TEXTURE_SNIPPET = `const root = useGlassRoot();

// The prop declares the source, so \`configuredSource\` stays true through any
// demotion. This hands over the pixels, which the platform-free core cannot hold.
root.setBackdropTexture("hero", { kind: "image", image });

<GlassGroup id="hero" backdrop={{ kind: "texture", id: "hero" }}>
  <GlassSurface radius={26} thickness={18} />
</GlassGroup>`;
