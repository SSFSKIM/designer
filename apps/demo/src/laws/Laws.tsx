/**
 * The material laws, one section each, live.
 *
 * Composed under `apps/demo/DESIGN.md` like the site at `/`: the narrative scrolls
 * in the left column, the right column is a fixed stage where the material is
 * actually running, and the stage follows what the reader is on. Each section is
 * one law the reference was measured to obey, stated in plain language, with a
 * control that lets the reader see it move and the runtime's own numbers beside
 * it. Every value in a readout is read from the runtime or evaluated from the
 * constants it publishes; nothing on this page is typed in.
 */

import {
  accessibilityRefractionCap,
  MATERIAL_SOURCE_SIZE,
  TINT_SHADE,
} from "@vitreajs/vitrea-web";
import {
  PlanePortal,
  useGlassAccessibility,
  type AccessibilityOverride,
} from "@vitreajs/vitrea-react";
import { useEffect, useMemo, useState, type ReactNode } from "react";

import { DiagnosticsReadout, GroupReadout } from "../site/Readout";
import { ChannelReadout } from "./ChannelReadout";
import { bodyLaw, fixed, TONE_SPANS, toneLaw } from "./law";
import { GROUPS_BY_MODE, LawsGlass, LawsGround, NEST, TINT_GROUNDS, type LawMode } from "./LawsStage";

export interface LawsProps {
  readonly requestedRenderer: "css" | "webgpu";
  /** Owned above, because it is a `GlassRoot` construction prop. */
  readonly reducedTransparency: AccessibilityOverride;
  readonly onReducedTransparencyChange: (next: AccessibilityOverride) => void;
}

interface SectionSpec {
  readonly id: string;
  readonly title: string;
  readonly mode: LawMode;
}

const SECTIONS: readonly SectionSpec[] = [
  { id: "tone", title: "Taking the tone of the backdrop, on a curve", mode: "tone" },
  { id: "tint", title: "A tint is a shade of its seed", mode: "tint" },
  { id: "body", title: "Two components in the body", mode: "body" },
  { id: "lens", title: "The lens reads the body", mode: "lens" },
  { id: "nested", title: "Glass over glass", mode: "nested" },
];

/**
 * The tone control's stops, in integer thousandths of linear luminance for the
 * site's reason: a range input validates against `min + n * step` in binary
 * floating point, and a fractional grid rejects most of its own positions.
 *
 * Black to white, the whole axis, because the response curve spans the whole
 * axis: its anchors sit at encoded means of 0.11, 0.27 and 0.95.
 */
const TONE_GROUND = { min: 2, max: 1000, step: 2, initial: 300 } as const;

/** The body control's stops: the size law's floor, past the scatter's ceiling. */
const BODY_SPAN = { min: 32, max: 288, step: 4, initial: 112 } as const;

const RUNGS = [
  { value: "true", label: "true: the WebGPU tier over a texture, at nominal policy" },
  { value: "approximate", label: "approximate: reduce transparency on" },
  { value: "none", label: "none: the CSS tier" },
] as const;

type Rung = (typeof RUNGS)[number]["value"];

/** `#rrggbb` to the `rgb(r g b / s%)` form the tint API takes, alpha as strength. */
function seedColour(hex: string, strength: number): string {
  const value = Number.parseInt(hex.replace("#", ""), 16);
  const r = (value >> 16) & 255;
  const g = (value >> 8) & 255;
  const b = value & 255;
  return `rgb(${r} ${g} ${b} / ${strength}%)`;
}

function useActiveSection(): string {
  const [active, setActive] = useState<string>(SECTIONS[0]?.id ?? "tone");

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

/** Reloads with a different query, because a root wires its renderer once. */
function navigate(renderer: "css" | "webgpu", rung?: Rung): void {
  const url = new URL(window.location.href);
  url.searchParams.set("renderer", renderer);
  if (rung === "approximate") url.searchParams.set("rung", rung);
  else url.searchParams.delete("rung");
  window.location.assign(url.toString());
}

export function Laws(props: LawsProps): ReactNode {
  const policy = useGlassAccessibility();
  const active = useActiveSection();
  const [toneStep, setToneStep] = useState<number>(TONE_GROUND.initial);
  const [seed, setSeed] = useState<string>("#ff9500");
  const [strength, setStrength] = useState<number>(100);
  const [bodySpan, setBodySpan] = useState<number>(BODY_SPAN.initial);

  const mode = useMemo<LawMode>(
    () => SECTIONS.find((section) => section.id === active)?.mode ?? "tone",
    [active],
  );

  const toneLevel = toneStep / 1000;
  const tone = toneLaw(toneLevel);
  const tint = seedColour(seed, strength);
  const cap = policy === undefined ? "true" : accessibilityRefractionCap(policy.material);
  const body = bodyLaw(bodySpan, MATERIAL_SOURCE_SIZE.refractionScale[cap]);
  const rung: Rung =
    props.requestedRenderer === "css" || cap === "none"
      ? "none"
      : cap === "approximate"
        ? "approximate"
        : "true";

  const stageProps = {
    mode,
    toneLevel,
    tint,
    bodySpan,
    animate: policy?.reducedMotion !== true,
  } as const;

  return (
    <>
      <LawsGround {...stageProps} />

      <main className="column">
        <header className="masthead">
          <p className="wordmark">vitrea</p>
          <h1 className="display">The material laws</h1>
          <p className="lead">
            Five things the reference material does that vitrea now does too, each
            measured against captures of Apple&rsquo;s own renderer before it was
            written into the material. One law per section, running live in the
            window on the right, on whatever tier this browser can give it.
          </p>
          <p className="body">
            Every number in a readout is read from the runtime or evaluated from the
            constants it publishes. Where a law reaches only the WebGPU tier the
            section says so, and the CSS tier still renders the honest version.
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
              <li>
                <a href="../">Back to the site</a>
              </li>
            </ul>
          </nav>
          <Fields legend="Renderer">
            <RendererField requested={props.requestedRenderer} />
          </Fields>
        </header>

        <Section spec={SECTIONS[0]} active={active}>
          <p className="body">
            Liquid Glass takes the tone of what is behind it. Swept across solid and
            patterned backdrops from black to white, the reference settles its
            interior on one curve of the backdrop&rsquo;s level: a monotone curve
            through three measured anchors, whose ends move with the surface&rsquo;s
            size. It reads that level as the mean taken in encoded sRGB, not in
            linear light. The difference only shows over structured content, where
            an average taken before a non-linearity is not the average after it.
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
                value={toneStep}
                onChange={(event) => setToneStep(Number(event.target.value))}
                aria-valuetext={`${toneLevel.toFixed(3)} linear`}
                data-testid="tone-level"
              />
              <span className="field__hint" data-testid="tone-level-readout">
                {toneLevel.toFixed(3)} linear, {fixed(tone.encoded)} encoded. The
                anchors sit at 0.110, 0.271 and 0.951 encoded.
              </span>
            </label>
          </Fields>
          <p className="body">
            Drag the ground from black to white. The 40px plate follows the curve
            almost all the way; the 112px plate holds more of its own appearance at
            every stop, because the anchors&rsquo; settled levels are functions of
            size. The near-black end is the collapse the material already had,
            byte for byte.
          </p>
          <dl className="readout" data-testid="tone-law">
            <div className="readout__head">
              <dt>The law</dt>
              <dd>evaluated from the published curve</dd>
            </div>
            <div className="readout__row">
              <dt>Encoded mean the law reads</dt>
              <dd>{fixed(tone.encoded)}</dd>
            </div>
            <div className="readout__row">
              <dt>Interior it targets, {TONE_SPANS.small}px</dt>
              <dd>{fixed(tone.small)}</dd>
            </div>
            <div className="readout__row">
              <dt>Interior it targets, {TONE_SPANS.large}px</dt>
              <dd>{fixed(tone.large)}</dd>
            </div>
          </dl>
          <ChannelReadout label="the 40px plate" testId="tone-small" />
          <ChannelReadout label="the 112px plate" testId="tone-large" />
          {GROUPS_BY_MODE.tone.map((group) => (
            <GroupReadout key={group.id} id={group.id} label={group.label} />
          ))}
          <p className="note">
            On the CSS tier the read is one mean per backdrop source, taken in the
            same space. On the WebGPU tier it is per pixel, corrected so its mean
            matches the model exactly. Reduce transparency and increase contrast
            keep the behaviour they were fitted to: the law rides only the
            un-degraded material.
          </p>
          <DiagnosticsReadout />
        </Section>

        <Section spec={SECTIONS[1]} active={active}>
          <p className="body">
            A tint is not a wash. Read per pixel, the reference&rsquo;s tinted
            material is an opaque, hue-preserving shade of the seed whose
            brightness follows the untinted material&rsquo;s own local luminance,
            composited over the material at the strength the author gave. Where
            the untinted material would be black the shade sits at{" "}
            {fixed(TINT_SHADE.dark, 2)} of the seed; where it would be white, at the
            seed itself. A light material over dark content is nowhere near black,
            so two plates over two grounds differ by less than the ends of that
            range do, and they differ in the direction the reference does.
          </p>
          <Fields legend="Tint">
            <label className="field">
              <span className="field__label">Seed</span>
              <input
                className="field__swatch"
                type="color"
                value={seed}
                onChange={(event) => setSeed(event.target.value)}
                data-testid="tint-seed"
              />
            </label>
            <label className="field">
              <span className="field__label">Strength</span>
              <input
                className="field__range"
                type="range"
                min={0}
                max={100}
                step={5}
                value={strength}
                onChange={(event) => setStrength(Number(event.target.value))}
                aria-valuetext={`${strength} per cent`}
                data-testid="tint-strength"
              />
              <span className="field__hint" data-testid="tint-readout">
                {tint}. The colour&rsquo;s alpha is the strength, which is how the
                API takes it.
              </span>
            </label>
          </Fields>
          <p className="body">
            The two plates carry the same colour at the same strength over the two
            halves of one ground, {fixed(TINT_GROUNDS.dark, 2)} and{" "}
            {fixed(TINT_GROUNDS.light, 2)} linear. At full strength each is an
            opaque shade, darker on the left than on the right. At half strength
            each is half shade and half material, and the ground comes through the
            material half.
          </p>
          <ChannelReadout label="over the dark half" testId="tint-dark" />
          <ChannelReadout label="over the light half" testId="tint-light" />
          {GROUPS_BY_MODE.tint.map((group) => (
            <GroupReadout key={group.id} id={group.id} label={group.label} />
          ))}
          <p className="note">
            The material&rsquo;s own opacity, the value reduce transparency and
            increase contrast operate on, does not change with the tint: the
            policies resolve first and the shade composites after. The CSS tier
            folds the shade into its one rgba layer exactly, which is also what
            removed the gamut clip a saturated seed could hit there. On the dark
            scheme the layer is the pure seed, because the reference shades the
            tint only on the light material.
          </p>
        </Section>

        <Section spec={SECTIONS[2]} active={active}>
          <p className="body">
            What you see through the glass has two components. The
            reference&rsquo;s interior is not one Gaussian blur. A sharp blur at{" "}
            {fixed(body.sharp, 2)} px keeps the structure of the content behind, the
            edges of text and the cells of a pattern, and a much wider scatter at{" "}
            {fixed(body.scatter, 1)} px lays a haze over it. The two are mixed by an
            amount that starts at a floor on any surface and grows with the
            surface&rsquo;s short span, on the same size law the thickness facets
            ride.
          </p>
          <Fields legend="Surface">
            <label className="field">
              <span className="field__label">Short span</span>
              <input
                className="field__range"
                type="range"
                min={BODY_SPAN.min}
                max={BODY_SPAN.max}
                step={BODY_SPAN.step}
                value={bodySpan}
                onChange={(event) => setBodySpan(Number(event.target.value))}
                aria-valuetext={`${bodySpan} pixels`}
                data-testid="body-span"
              />
              <span className="field__hint" data-testid="body-span-readout">
                {bodySpan}px. The mix starts at {fixed(MATERIAL_SOURCE_SIZE.sizeScatterFloor, 2)} and
                saturates at {MATERIAL_SOURCE_SIZE.sizeScatterSpanMax}px.
              </span>
            </label>
          </Fields>
          <p className="body">
            Drag the span. The text behind the plate stays legible at every size,
            and the haze over it deepens as the plate grows. On the WebGPU tier the
            two components are mixed per pixel. The CSS tier has one backdrop-filter
            blur, so it takes a single width at the mixed value: its interior level
            matches, and its structure is the tier&rsquo;s known limit.
          </p>
          <dl className="readout" data-testid="body-law">
            <div className="readout__head">
              <dt>The law</dt>
              <dd>evaluated from the published constants</dd>
            </div>
            <div className="readout__row">
              <dt>Scatter mix at this span</dt>
              <dd>{fixed(body.mix)}</dd>
            </div>
            <div className="readout__row">
              <dt>Sharp component</dt>
              <dd>{fixed(body.sharp, 2)} px</dd>
            </div>
            <div className="readout__row">
              <dt>Scatter component</dt>
              <dd>{fixed(body.scatter, 2)} px</dd>
            </div>
            <div className="readout__row">
              <dt>CSS tier, single width</dt>
              <dd data-testid="body-single">{fixed(body.single, 2)} px</dd>
            </div>
          </dl>
          <ChannelReadout label="the plate" testId="body-plate" />
          {GROUPS_BY_MODE.body.map((group) => (
            <GroupReadout key={group.id} id={group.id} label={group.label} />
          ))}
        </Section>

        <Section spec={SECTIONS[3]} active={active}>
          <p className="body">
            The rim refracts. Measured per one-pixel depth shell around the whole
            contour, the reference&rsquo;s band displaces the backdrop inward on the
            lens profile vitrea already had, a (1 &minus; depth)&sup2; curve over
            the lens depth, at 1.6 times the displacement the previous material
            used. It reads the same two-component body as the interior: no extra
            blur, no sharper rim, no darkening.
          </p>
          <Fields legend="Refraction">
            <label className="field">
              <span className="field__label">Rung</span>
              <select
                value={rung}
                onChange={(event) => {
                  const next = event.target.value as Rung;
                  if (next === "none") {
                    navigate("css");
                  } else if (props.requestedRenderer === "css") {
                    navigate("webgpu", next);
                  } else {
                    props.onReducedTransparencyChange(next === "approximate");
                  }
                }}
                data-testid="lens-rung"
              >
                {RUNGS.map((entry) => (
                  <option key={entry.value} value={entry.value}>
                    {entry.label}
                  </option>
                ))}
              </select>
              <span className="field__hint">
                Moving to or from the CSS tier reloads the page: a root wires its
                renderer once, at construction.
              </span>
            </label>
          </Fields>
          <p className="body">
            The rung is a policy result, not a knob. The WebGPU tier over a
            registered texture lenses for real, <code>true</code>. Reduce
            transparency caps it at <code>approximate</code>, the rim-only bend,
            which is also what the tier can honestly claim over page content it
            samples through a proxy. The CSS tier carries no lens at all,{" "}
            <code>none</code>: backdrop-filter blurs and never bends. Choosing a
            rung here changes the policy or the tier, and the readout says which.
          </p>
          <dl className="readout" data-testid="lens-policy">
            <div className="readout__head">
              <dt>Resolved policy</dt>
              <dd>read from the runtime</dd>
            </div>
            <div className="readout__row">
              <dt>Refraction regime</dt>
              <dd data-testid="lens-regime">{policy?.material.refraction ?? "none"}</dd>
            </div>
            <div className="readout__row">
              <dt>Cap on the ladder</dt>
              <dd data-testid="lens-cap">{cap}</dd>
            </div>
            <div className="readout__row">
              <dt>Frost</dt>
              <dd>{policy?.material.frost ?? "none"}</dd>
            </div>
          </dl>
          {GROUPS_BY_MODE.lens.map((group) => (
            <GroupReadout key={group.id} id={group.id} label={group.label} />
          ))}
          <p className="note">
            Reduce transparency does more than cap the rung: it frosts harder and
            occludes more, which is what the preference asked for. The plate under
            the approximate rung is the whole preference, not the lens alone.
          </p>
        </Section>

        <Section spec={SECTIONS[4]} active={active}>
          <p className="body">
            A pane over glass composites over the glass beneath it. The
            reference&rsquo;s upper pane in this arrangement reads at about 0.89 of
            white; the previous material drew it at a flat 0.47, because a surface
            with nothing to sample wrote its material mixed over black and opaque.
            It now leaves as a premultiplied layer at the material&rsquo;s alpha,
            with the outer shadow clipped to its coverage, and the browser
            composites it in the same encoded space the CSS tier&rsquo;s rgba
            lands in.
          </p>
          <p className="body">
            The geometry is <code>scenes.json</code>&rsquo;s own: a {NEST.base.width}
            &times;{NEST.base.height} base and a {NEST.over.width}&times;
            {NEST.over.height} pane centred on it and lifted {-NEST.over.offsetY}px.
            The base surface samples the registered texture. The pane sits on the
            overlay plane in a group of its own with no texture to sample, so on the
            WebGPU tier it resolves to backdrop-filter sampling through a proxy,{" "}
            <code>css-backdrop</code> at <code>approximate</code>, which is not a
            fault and is named as one would be. On the CSS tier both filter in
            place, and the pane simply blurs the glass under it.
          </p>
          {GROUPS_BY_MODE.nested.map((group) => (
            <GroupReadout key={group.id} id={group.id} label={group.label} />
          ))}
          <ChannelReadout label="the pane" testId="nested-over" />
          <DiagnosticsReadout />
          <p className="note">
            The pane is not inside the base surface&rsquo;s content. It is a
            separate host on a separate plane, which is the composition the layer
            model allows and the one the reference was captured in.
          </p>
        </Section>

        <footer className="footer">
          <p className="note">
            Apache-2.0. Liquid Glass and macOS are trademarks of Apple Inc.; vitrea
            is an independent implementation and is not affiliated with or endorsed
            by Apple.
          </p>
          <p className="note">
            <a href="../">The site</a> tells the story of the runtime; this page
            tells the story of the material. The measurements behind each law are
            in the repository&rsquo;s fidelity claims.
          </p>
        </footer>
      </main>

      {/*
        One portal per plane, each holding a whole mirror of the stage, so the
        stage's layout survives the move into the plane's host layer and the two
        planes' surfaces line up by construction.
      */}
      <PlanePortal plane="base">
        <LawsGlass {...stageProps} plane="base" />
      </PlanePortal>
      <PlanePortal plane="overlay">
        <LawsGlass {...stageProps} plane="overlay" />
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

function RendererField(props: { readonly requested: "css" | "webgpu" }): ReactNode {
  return (
    <label className="field">
      <span className="field__label">Requested renderer</span>
      <select
        value={props.requested}
        onChange={(event) => navigate(event.target.value === "css" ? "css" : "webgpu")}
        data-testid="renderer-select"
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
