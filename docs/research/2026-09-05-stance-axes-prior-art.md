# Stance axes: prior art, a ranked axis set, generative-diversity evidence, and risks

*Research memo, 2026-09-05. Source material for the `designer` plugin; never loaded at runtime.
Written for the decision to replace "pick a named system and port its token block" with
"derive a stance from a small set of axes, and key every downstream table by axis position".
Six parallel web-research tracks verified the sources below against primary pages; claims a
track could not confirm are marked "recalled, not verified".*

## 0. What the current catalogue actually spans

Before the prior art, a measurement of the five complete systems in
`skills/designer/references/stances.md`, converted to OKLCH:

| System | Ground L / C / hue | Accent L / C / hue | Body px | Space base | Radius-4 | Fast / slow ms |
|---|---|---|---|---|---|---|
| Precision industrial | 0.972 / 0.003 / 229 | 0.641 / 0.151 / 48 | 15 | 4/8/12/16 | 8 | 120 / 240 |
| Quiet editorial | 0.957 / 0.012 / 80 | 0.522 / 0.136 / 35 | 16 | 4/8/12/16 | 12 | 160 / 420 |
| Craft commerce | 0.930 / 0.016 / 83 | 0.573 / 0.127 / 39 | 15 | 4/8/12/16 | 16 | 150 / 360 |
| Institutional calm | 0.975 / 0.005 / 106 | 0.534 / 0.076 / 192 | 16 | 4/8/12/16 | 10 | 140 / 300 |
| Playful consumer | 0.975 / 0.013 / 295 | 0.832 / 0.145 / 75 | 16 | 4/8/12/16 | 20 | 140 / 420 |

Three things follow. The catalogue has zero spread on ground lightness (every ground sits in
L 0.93–0.975) and zero spread on density (one spacing scale, body 15–16 px, label 11–12 px).
Three of the five accents sit in OKLCH hue 35–48, which is the terracotta band that
`taste-calibration.md` names as the first saturated AI default. Its variance lives in hue family,
type family, radius and easing, which are the axes that least affect fit to a brief. That is the
mechanical reason a dispatch console and a gym page could ship identical: the two axes on which
they should differ most are constants of the catalogue.

## 1. Prior art: design as a position on a few axes

| Source | Axes | Independence shown? | Concrete parameters tied |
|---|---|---|---|
| Osgood 1964; Osgood, May & Miron 1975 (semantic differential) | Evaluation, Potency, Activity | Yes, factor analysis, replicated across ~two dozen language communities | None; it is the measuring instrument every later row uses |
| Nagamachi 1995 (Kansei engineering) | Domain-specific; extracted per product by factor analysis | Per study, not a fixed set | Adjective → design-element level via Quantification Theory I (partial correlation per element, category score per level) |
| Ou, Luo, Woodcock & Wright 2004; Ou et al. 2018 (colour emotion) | Colour activity, colour weight, colour heat | Yes; 2018 replication across 12 regions, r 0.78–0.81 | CIELAB equations: weight ≈ f(100−L*) + cos(h−100°); heat ≈ C*^1.07·cos(h−50°); activity = distance from a drab anchor at L 50, a 3, b 17. Coefficients came from search extraction of closed-access PDFs, re-verify before hard-coding |
| Valdez & Mehrabian 1994 (PAD) | Pleasure, Arousal, Dominance | Regression on Munsell chips | Pleasure = .69·Brightness + .22·Saturation; Arousal = −.31B + .60S; Dominance = −.76B + .32S; hue far weaker |
| Kobayashi 1981/1991 (Color Image Scale) | Warm–cool, soft–hard, clear–grayish | Weak; one 1981 methods paper, no published loadings | Adjective positions are centroids of 3-colour combinations; needs Munsell→Lab conversion to use |
| Aaker 1997; Labrecque & Milne 2012 (brand personality → colour) | Sincerity, Excitement, Competence, Sophistication, Ruggedness | Aaker yes (factor analysis, N 631); hue mapping unstable across studies (Ridgway & Myers 2014 differs) | Saturation ↑ → exciting, rugged; value ↑ → sincere, sophisticated; blue → competence, red → excitement |
| Lavie & Tractinsky 2004 (web aesthetics) | Classical (clean, orderly) vs Expressive (creative, original) | Distinct factors, but correlated r = 0.61 in CFA | None directly; classical correlates 0.60–0.78 with usability and trust, expressive only 0.37–0.59 |
| Moshagen & Thielsch 2010 (VisAWI) | Simplicity, Diversity, Colorfulness, Craftsmanship | Four facets under one general factor, r 0.60–0.74 | Colour-scheme manipulation moved only Colorfulness; Simplicity ↔ Classical, Diversity ↔ Expressive |
| Reinecke et al. CHI 2013; Tuch et al. 2012 | Visual complexity, colorfulness (+ prototypicality) | Separate measured predictors | Complexity from text/non-text area and group counts predicts appeal (adj R² .48, complexity dominates, age-moderated); low complexity + high prototypicality most appealing |
| Henderson, Giese & Cote 2004; Grohmann et al. 2013 (typeface) | Impressions: pleasing, engaging, reassuring, prominent | Trade-offs stated; response surfaces recalled, not verified | Design characteristics elaborate, harmony, natural, flourish, weight, compressed; weight is the discriminating lever (heavy → competence/ruggedness, light → sincerity/sophistication) |
| Shaikh, Chaparro & Fox 2006; O'Donovan et al. 2014 (font attributes) | 15 trait pairs; 37 crowd attributes | Not independent: O'Donovan's metric embedding chose 7 dimensions, strong/thin r = −0.95 | Class predicts trait profile; sans serif is extreme on nothing; script scores 2–3% for spreadsheets or code |
| Lockyer & Bartram 2012; Feng, Bartram & Gromala 2017 (affective motion) | Speed, path curvature, direction, shape | Factorial design, N 12 | Speed significant on all five affect scales; straight vs not-straight is binary; inward attracts |
| IBM Carbon | Theme (4), layer, productive vs expressive, size | Theme claimed orthogonal; register explicitly not | Base 14 vs 16 px, tracking +0.16/+0.32 → 0, fixed vs fluid headings, easing (0.2,0,0.38,0.9) vs (0.4,0.14,0.3,1); durations shared 70–700 ms |
| Material Design 3 / M3 Expressive 2025 | Seed, variant, dark, contrast level; density integer; standard vs expressive | Not claimed; shape ↔ type coupling stated | −4 px per density step; 9 scheme variants as chroma/hue rules (tonalSpot chroma 36, vibrant 200, expressive hue+240°); emphasized type = weight +1 step, tracking → 0, size unchanged; expressive springs only on spatial motion (damping 0.9 → 0.8/0.6) |
| Apple HIG (2013 themes; Materials; Liquid Glass 2025) | Clarity, deference, depth; thickness × appearance; functional vs content layer | Interactions documented, not independence | Four materials + chrome; regular vs clear glass; 35% dimming over bright content; never in the content layer; concentric radii |
| Microsoft Fluent 2 | Global/alias tokens, brand ramp, shadow integer, per-component size | Constraints published instead | Shadow n → blur n px, y n/2; radius 0–40 + circular; materials solid/mica/acrylic/smoke; "don't apply backdrop material more than once" |
| Adobe Spectrum | Platform scale, colour theme, t-shirt size | Structurally yes (token `sets`), interactions in prose | Desktop:mobile 1:1.25; shadow opacity rises in dark themes |
| Radix Themes | appearance, accent, gray, panelBackground, radius, scaling | Mostly; accent auto-pairs a gray | scaling 0.9–1.1 multiplies 33+ tokens; radius factor 0/0.75/1/1.5/1.5; discrete levels only |
| Atlassian | Voice: bold, optimistic, practical-with-a-wink (three, not four); emphasis; elevation; light/dark | Explicitly denied (elevation × theme) | Dark-mode elevation via lighter surfaces; density named as future work |
| NN/g tone of voice (Moran 2016) | Formal–casual, serious–funny, respectful–irreverent, matter-of-fact–enthusiastic | 4-D space asserted, never tested | Trust explains 52% of desirability variance, friendliness adds 8%; humour can lower trust |
| Enterprise density (Salesforce, Ant, Primer, Gmail, Jira) | 2–3 named steps or a seed multiplier | Primer's density × size cross cleanly; Salesforce's flips label placement | Ant controlHeight 32 × 0.75/1/1.25, compact = −4 px and small font; Primer padding 8/12/16; Salesforce compact puts labels inline |
| Marks et al. 1997 (Design Galleries); Swearngin et al. CHI 2020 (Scout) | Parameter vector → output vector | n/a | Disperse in output space, not parameter space; Scout: high-level constraints gave 18 designers more diverse layouts at similar quality |

What recurs. Across Osgood, Ou, Valdez and Kobayashi the same triad appears with the same
physical carriers: lightness carries weight, potency and dominance; chroma carries activity and
arousal; hue carries warm–cool and almost nothing else. The web-aesthetics instruments converge
on a single order-versus-richness pair, which is what Carbon calls productive/expressive and
Material calls standard/expressive, and that pair is correlated at roughly r 0.6, not orthogonal.
Every shipped system exposes its axes as discrete named levels, never sliders.

## 2. Recommended axis set, ranked

Ranking weighs evidence strength, how much fit-relevant spread the axis buys, and how many
downstream token families it drives. Rungs are discrete and named; two axes deliberately have
no middle rung.

| # | Axis | Rungs | Token families driven | Checkable rules |
|---|---|---|---|---|
| 1 | **Register** (productive ↔ expressive) | productive, productive-leaning, expressive-leaning, expressive (no middle) | type weight and tracking, emphasized styles, fixed vs fluid headings, spatial motion damping and easing, accent chroma ceiling, radius scale, shape language, illustration licence, copy posture | Productive: small text (≤ 14 px) carries positive tracking; display weight 300–600; headings fixed across breakpoints; spatial motion critically damped (Apple bounce 0, damping ≥ 0.9, Carbon productive curve); accent C ≤ 0.15; control radius ≤ 6 px; copy formal and matter-of-fact. Expressive: at least one emphasized role one weight step up with tracking reduced toward 0; display tracking ≤ 0 (Carbon −0.64 px at 60–92 px); fluid display via clamp; spatial springs damping 0.6–0.8 or bounce 0.15–0.30, never above 0.4; effects (colour, opacity) stay critically damped regardless; accent C up to 0.22; radius ≥ 10 px or a declared shape language. **Overshoot** is a separate recorded yes/no: IBM forbids bounce even in expressive, Google and Apple build expressive on it |
| 2 | **Density** (spacious ↔ dense) | spacious, standard, dense (the middle is a real product default, must be picked by task type and recorded) | space base and steps, body and label size, control and row height, label placement, type-scale ratio, containment method, accent coverage | Dense: body 13–14 px, control height 28–32, row ≤ 36, base unit 4 favouring 4/8/12/16, labels inline, containment by hairline or tone not shadow, in-app display ≤ 32 px, accent coverage ≤ 5%. Spacious: body 16–18, control 40–48, steps favour 8/16/24/32/48, labels above fields, scale ratio ≥ 1.25. Never reduce touch targets below default on touch surfaces |
| 3 | **Ground lightness** (light ↔ dark) | light, dark (optional "dim" mid-tone body counts as dark for rules) | background/foreground roles, surface layering, border alpha, shadow opacity, accent lightness floor, material resolution | Dark: elevation by lighter surfaces (layer-01 lighter than ground), shadows demoted to overlays; accent L ≥ 0.62; borders as light alpha; contrast measured on the actual surface. Light: ground L ≥ 0.93 or a deliberately mid-tone brand body. Choice recorded by the scene sentence, never by register (dark is heavy and dominant per Valdez, not sober) |
| 4 | **Ground temperature** (warm ↔ neutral ↔ cool, plus brand-tinted) | warm, neutral, cool, brand-tinted | neutral ramp hue, border and shadow tint, cream-band check | All neutrals share one hue family within ±20° at C ≤ 0.02 (≤ 0.04 brand-tinted); borders and shadows are the foreground hue at alpha; a ground in the cream band (L 0.84–0.97, C < 0.06, h 40–100) needs a named justification; warm at C 0.003 is neutral by Ou's heat equation, so warmth must be carried by something with chroma (accent, imagery); warm is allowed at dark |
| 5 | **Material model** | flat, tonal-layered, elevated, glass-over-planes | shadow tiers, surface layer tokens, panel translucency, backdrop-filter, vibrancy, concentric radii | Flat: no shadows except popover and modal, containment by border and tone. Tonal-layered: ≤ 3 surface steps by lightness. Elevated: ≤ 3 shadow tiers generated from one integer (Fluent: blur n, y n/2), shadows on floating UI only. Glass: only a floating functional layer over changing content, never nested, 35% dimming over bright content, solid fallback, disallowed at dense register-productive content surfaces. Coupling: at dark, "elevated" resolves to tonal plus shadow |
| 6 | **Type class** (neutral ↔ characterful display), tradition as the nominal value | neutral sans, characterful serif, characterful display, mono-as-display | font-display, font-ui, font-mono, case behaviour | Display class must sit inside the register (productive: neo-grotesque, humanist, geometric, slab, transitional; expressive: any, including Didone or script); script and display faces never for body or UI; UI face is a sans or a humanist serif for reading products; mono only where a tabular role exists; at dense, positive tracking at ≤ 12 px; the existing swap-one-slot rule holds |
| 7 | **Colour commitment** (restrained ↔ drenched), already in taste-calibration | restrained, committed, full palette, drenched | accent coverage, number of colour roles, body as brand colour | Keep the existing percentages (≤ 10%, 30–60%, roles, surface). Chroma ceiling comes from register, coverage from commitment; dense forbids full palette and drenched |

Not axes. **Accent job** (action, selection, focus, status) is a role decision and stays a recorded
decision. **Trust or seriousness** is not an axis: in the evidence it is the classical pole of
register plus craftsmanship and prototypicality, and NN/g's data says trust drives desirability
while friendliness barely moves it, so trust belongs to the QA floor. **Motion register** is a
consequence of register: Material's effects springs are identical across schemes and Carbon's
durations are shared, so only spatial damping and the overshoot flag remain, and both live in
axis 1. **Emotional register (playful ↔ sober)** is axis 1 under another name.

Collapses to watch:

| Sounds orthogonal | What the evidence says | Rule that keeps them apart |
|---|---|---|
| Trust and density | Different things. Trust tracks order and craft; density raises complexity, which is the dominant negative predictor of appeal in Reinecke 2013 | Dense must pay with craftsmanship (alignment, one hairline weight, one accent), and "serious ⇒ dense" is refused; Institutional calm is spacious and serious |
| Sober and dark | Uncorrelated. Dark reads heavy and dominant, not sober; terminal-dark is the second-order reflex the skill already names | Lightness is chosen by scene, and the record must not cite register as the reason |
| Playful and high chroma | Chroma is arousal, so register sets a ceiling; Apple is expressive at low chroma through shape and motion | Register never raises chroma by itself; commitment and accent job do |
| Warm and cream | A training-data correlation, not a law | Warm at dark or at mid-tone is a first-class option; the cream band needs a justification |
| Material and lightness | Coupled in every system: shadows vanish on dark, surfaces lighten instead | The resolution table maps (material, lightness) to the surface recipe |
| Material and density | Coupled by the layer rule: glass belongs to a floating layer, never to dense content | Glass is disallowed at dense |

Archetypes stay, as worked derivations. A named stance becomes an axis vector plus one or two
signature constraints written in derivation vocabulary, the way Material's scheme variants are
rules over the seed ("primary chroma at maximum", "tertiary hue rotated") rather than hex blocks:

| Stance | Register | Density | Lightness | Temperature | Material | Type class | Commitment | Signature constraint |
|---|---|---|---|---|---|---|---|---|
| swiss | productive | standard | light | neutral-cool | flat | neo-grotesque | restrained | strict modular grid; one accent |
| terminal | productive | dense | dark | cool | flat | mono-as-display | restrained | one phosphor accent carries all signal |
| editorial | expressive-leaning | spacious | light | warm | tonal-layered | characterful serif | restrained | asymmetric measure; display tracking ≤ 0 |
| memphis | expressive | spacious | light | warm pastel | flat | display sans | full palette | primary geometric shapes as structure |
| kinetic | expressive | standard | dark | neutral | elevated | neo-grotesque | committed | overshoot yes; motion marks every state change |

Any brief then derives its own vector; a named stance is a precedent, not a template, and its
values are recomputed from the brief's positions.

## 3. Evidence on generative diversity

There is no study that compares named-look sampling with axis-position sampling for UI
generation. The choice is underdetermined; the case for axes is three converging indirect lines.

Convergence is real and shared. Jiang et al., NeurIPS 2025 (Artificial Hivemind), show
inter-model homogeneity across 70+ models on 26,000 open-ended prompts. Padmakumar & He, ICLR
2024, and Kirk et al., ICLR 2024, locate the loss in preference tuning. Zhang et al. 2025
(Verbalized Sampling) name typicality bias in preference data as the driver and recover 1.6–2.1×
diversity by asking for a distribution. Imteyaz et al., AAAI/AIES 2026 (Design Theater), is the
only quantified UI result: across five tools on 24 tasks, visual and layout distance were nearly
invariant while colour varied almost twofold. Anthropic's own frontend-design skill lists
editorial-cream and broadsheet, both named looks, as the current defaults appearing "regardless
of subject".

Where variation is injected decides whether it reaches the output. Zhang, Xin & Zhong 2026 measure
a transmission score: specification-level variation reaches the output at 0.46–0.55, random
surface injection at 0.003, and random injection scored below plain prompting on an open-ended
bed (LLM-judged diversity 2.40 vs 2.69 direct vs 7.32 for specification-level). Yu et al., NeurIPS
2023, found attributed prompts beat class-conditional prompts; Deng, Brucks & Toubia 2026 found
ordinary distributed personas beat a famous named persona; Feng, Hélie & Panchal 2025 found one
design per conditioning vector beats one prompt asking for several; Fu et al. 2026 found models
learn more reliably from rules than from examples. Against this, Agrawal & Goyal 2026 found random
concepts do raise diversity on pure enumeration with no fit requirement, and Howard et al. 2011
found in humans that guided stimuli beat random ones for generating ideas while random stimuli
were "particularly good at removing mental blocks".

Concrete exemplars copy their surface. Min et al., EMNLP 2022: demonstrations transmit format and
vocabulary far more than content. Yun et al., EMNLP 2025: format scaffolding alone roughly halves
semantic diversity. Wadinambiarachchi et al., CHI 2024: one concrete reference propagated about a
third of its features into designers' sketches, and a generative tool amplified it. In the human
fixation literature, Jansson & Smith 1991 found copied features persist even under instructions
not to copy, and Ezzat et al. 2020 found the same examples stated abstractly reduce fixation and
double creative output while stated specifically they increase it; Ward, Patterson & Sifonis 2004
found abstract task framing yields more novel outputs. This is the mechanism behind the identical
hex: a verbatim token block is the most concrete exemplar possible.

Axis systems that exist. Suh et al., CHI 2024 (Luminate) sample values across LLM-generated
dimensions to produce diverse outputs; evaluation is qualitative, and they dropped numerical
dimensions after pilots found them unhelpful, keeping ordinal and nominal ones. Chen, Shi & Chen
2025 (SpecifyUI) parameterise layout, colour, shape and usage into a structured spec and beat
Google Stitch with 16 designers on style consistency (5.52 vs 4.18) and controllability, but
measure fit, not diversity. Swearngin et al., CHI 2020 (Scout) is the one study measuring both:
raising input to high-level constraints gave more diverse layouts at similar quality.

Two counterweights. Vasconcelos et al. 2017 found in humans that an abstract property fixated as
much as a concrete example, only on different ideas (recalled, not verified, paywalled). Rupprecht
et al. 2025 found larger models shift toward the centre of a scale when a middle option exists.
IDEAFix 2026 finds homogenization persists across every prompting intervention tested. Expect
reduction, not elimination.

Verdict. "Sample named looks" has no evidence behind it and one production counter-signal: the
named looks themselves became the defaults. "Sample axis positions" has mechanistic support
(specification-level variation transmits, abstract framing de-fixates, rules beat examples) and
one direct design analogue (Scout), but no UI diversity measurement. The experiment that would
settle it is cheap: three arms (named looks, axis vectors, named looks under verbalized sampling),
quality by human pairwise judgment on UI-Bench's protocol rather than a vision-language judge
(frontier models pick the best and worst image correctly 26.5% of the time vs 68.9% for experts,
Visual Aesthetic Benchmark 2026), diversity by Design Theater's three homogeneity indices, and the
headline metric Shypula et al. 2025's effective semantic diversity: spread among the outputs that
actually fit the brief, because raw spread flatters the named-look arm.

## 4. Risks of the axis approach, and the reconciliation

1. **Safe-default collapse.** Material 3's default variant is documented as "pastel palettes with
   a low chroma", and the 2018 "blanding" critique is exactly an axis system with every axis at
   the safe middle. Google's fix was named variants that push the derivation to a pole. Rule: no
   axis has an unlabelled default; the record must state each position and why.
2. **Midpoint attraction in the generator.** Rupprecht et al. 2025. Luminate dropped numeric
   dimensions. Rule: discrete named rungs, an even count with no middle where the middle is not a
   real product state (register), and a required brief-derived reason where it is (density).
3. **Incoherent corners.** Axes chosen independently produce points no style occupies; classical
   and expressive are correlated at r 0.6, and font attributes collapse to about seven dimensions.
   Rule: a coupling table (the collapses above) and archetypes as worked derivations, so the agent
   sees which corners are inhabited.
4. **Malicious spread.** Marks et al. 1997 found dispersion buys spread through degenerate
   extremes unless output coordinates are normalised. Rule: disperse in output space with a ledger
   of recent builds (accent hue, display size, families, density rung), not by maximising axis
   distance.
5. **Relocated fixation.** The axis vocabulary becomes the new attractor: every "expressive"
   build reaching for the same display face and spring. Rule: the existing swap-one-slot rule,
   applied per axis, and the ledger check.
6. **Perception is not preference.** Reinecke 2013: perception of complexity and colorfulness is
   universal, preference is moderated by age and education; Palmer & Schloss 2010: the Ou factors
   explain 55% of colour preference and object associations 80%. The axes predict what a design
   reads as, not whether the audience likes it; that is the brief's job.
7. **Framework defaults underneath the tokens.** Goree et al., CHI 2021, measured a >30% fall in
   layout distance across 10,000 sites and attributed it to library defaults. A derivation that
   leaves Tailwind or shadcn radii, grays and shadows in place will converge beneath the tokens.
   Rule: the derivation overrides the framework's radius, gray and shadow scales explicitly.

The reconciliation practitioners converge on: the archetype is a named rule over the derivation,
in the derivation's own vocabulary, never a values block. Material's scheme variants, Radix's
discrete levels, Carbon's productive/expressive as a rule switch (fixed vs fluid headings), Brad
Frost's "recipes" tier, and Adobe promoting the Express theme into Spectrum 2's baseline all
follow that pattern. Named styles are already documented that way in design history: Swiss is a
correlated bundle of grid, sans, flush-left, asymmetry and objective photography.

## Sources

Affect and aesthetics: Osgood 1964 https://anthrosource.onlinelibrary.wiley.com/doi/10.1525/aa.1964.66.3.02a00880 · Nagamachi 1995 https://doi.org/10.1016/0169-8141(94)00052-5 · Ou et al. 2004 https://onlinelibrary.wiley.com/doi/abs/10.1002/col.20010 · Ou et al. 2018 https://onlinelibrary.wiley.com/doi/full/10.1002/col.22243 · Kobayashi 1981 https://onlinelibrary.wiley.com/doi/10.1002/col.5080060210 · Valdez & Mehrabian 1994 https://pubmed.ncbi.nlm.nih.gov/7996122/ · Palmer & Schloss 2010 https://www.pnas.org/doi/10.1073/pnas.0906172107 · Aaker 1997 https://journals.sagepub.com/doi/abs/10.1177/002224379703400304 · Labrecque & Milne 2012 https://doi.org/10.1007/s11747-010-0245-y · Lavie & Tractinsky 2004 https://www.ise.bgu.ac.il/faculty/noam/papers/04_tl_nt_ijhcs.pdf · Moshagen & Thielsch 2010 http://www.thielsch.org/download/paper/moshagen_2010.pdf · Reinecke et al. 2013 https://www.eecs.harvard.edu/~kgajos/papers/2013/reinecke13aesthetics.pdf · Tuch et al. 2012 https://doi.org/10.1016/j.ijhcs.2012.06.003 · Fogg et al. 2003 https://advocacy.consumerreports.org/research/how-do-people-evaluate-a-web-sites-credibility

Typography and motion: Henderson, Giese & Cote 2004 https://doi.org/10.1509/jmkg.68.4.60.42736 · Shaikh, Chaparro & Fox 2006 https://soma.sbcc.edu/users/russotti/113/personality_Shaikh.pdf · Grohmann, Giese & Parkman 2013 https://doi.org/10.1057/bm.2012.23 · O'Donovan et al. 2014 https://www.dgp.toronto.edu/~donovan/font/fontSelection.pdf · Kulahcioglu & de Melo 2018 https://aclanthology.org/L18-1010.pdf · Carbon type sets https://carbondesignsystem.com/elements/typography/type-sets/ · Carbon motion https://carbondesignsystem.com/elements/motion/overview/ · Material tokens (AndroidX TypeScaleTokens.kt, MotionTokens.kt, ExpressiveMotionTokens.kt) · Apple, Animate with springs https://developer.apple.com/videos/play/wwdc2023/10158/ · Fluent tokens https://github.com/microsoft/fluentui/tree/master/packages/tokens/src · Feng 2016 thesis https://summit.sfu.ca/_flysystem/fedora/sfu_migrate/14331/etd8422_CFeng.pdf · Willenskomer 2017 https://uxmag.com/articles/creating-usability-with-motion-the-ux-in-motion-manifesto

Design systems: Material colour https://m3.material.io/styles/color/system/how-the-system-works · material-color-utilities https://github.com/material-foundation/material-color-utilities · Angular Material density https://material.angular.dev/guide/theming · Apple materials https://developer.apple.com/design/human-interface-guidelines/materials · Adopting Liquid Glass https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass · Fluent 2 https://fluent2.microsoft.design/design-tokens · Spectrum platform scale https://spectrum.adobe.com/page/platform-scale/ · Radix Themes https://www.radix-ui.com/themes/docs/theme/overview · Atlassian voice and tone https://atlassian.design/foundations/content/voice-tone · NN/g tone dimensions https://www.nngroup.com/articles/tone-of-voice-dimensions/ · NN/g tone study https://www.nngroup.com/articles/tone-voice-users/ · DTCG format https://designtokens.org/tr/drafts/format/ · Curtis, naming tokens https://medium.com/eightshapes-llc/naming-tokens-in-design-systems-9e86c7444676

Design space and creativity: Card, Mackinlay & Robertson 1991 https://dl.acm.org/doi/10.1145/123078.128726 · Marks et al. 1997 https://www.merl.com/publications/docs/TR97-14.pdf · Swearngin et al. 2020 (Scout) https://arxiv.org/abs/2001.05424 · Dayama et al. 2020 (GRIDS) https://arxiv.org/abs/2001.02921 · Koyama et al. 2014 https://koyama.xyz/project/CrowdPoweredAnalysis/ · Jansson & Smith 1991 https://doi.org/10.1016/0142-694X(91)90003-F · Marsh, Landau & Hicks 1996 https://doi.org/10.3758/BF03201091 · Siangliulue et al. 2015 https://www.eecs.harvard.edu/~kgajos/papers/2015/siangliulue15providing.shtml · Ward 1994; Ward, Patterson & Sifonis 2004 (Creativity Research Journal 16(1)) · Ezzat et al. 2020 https://doi.org/10.1002/jocb.349 · Howard, Culley & Dekoninck 2011 https://doi.org/10.1080/09544821003598573 · Chan et al. 2011 https://doi.org/10.1115/1.4004396

Generative diversity: Zhang et al. 2025, Verbalized Sampling https://arxiv.org/abs/2510.01171 · Jiang et al. 2025, Artificial Hivemind https://arxiv.org/abs/2510.22954 · Padmakumar & He 2024 https://arxiv.org/abs/2309.05196 · Kirk et al. 2024 https://arxiv.org/abs/2310.06452 · Anderson, Shah & Kreminski 2024 https://arxiv.org/abs/2402.01536 · Deng, Brucks & Toubia 2026 https://arxiv.org/abs/2602.20408 · Imteyaz et al. 2026, Design Theater https://arxiv.org/abs/2607.22928 · Shin et al. 2026 https://arxiv.org/abs/2603.13036 · Romero et al. 2026 https://arxiv.org/abs/2605.15124 · Anthropic frontend-design skill https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md · Suh et al. 2024, Luminate https://arxiv.org/abs/2310.12953 · Chen, Shi & Chen 2025, SpecifyUI https://arxiv.org/abs/2509.07334 · Zhang, Xin & Zhong 2026 https://arxiv.org/abs/2606.10302 · Agrawal & Goyal 2026 https://arxiv.org/abs/2601.18053 · Feng, Hélie & Panchal 2025 https://doi.org/10.1017/dsj.2025.10037 · Yu et al. 2023 https://arxiv.org/abs/2306.15895 · Carichon et al. 2026, IDEAFix https://arxiv.org/abs/2606.00875 · Min et al. 2022 https://arxiv.org/abs/2202.12837 · Yun et al. 2025 https://arxiv.org/abs/2505.18949 · Wadinambiarachchi et al. 2024 https://arxiv.org/abs/2403.11164 · Fu et al. 2026 https://arxiv.org/abs/2609.03213 · Rupprecht et al. 2025 https://arxiv.org/abs/2507.07188 · Shypula et al. 2025 https://arxiv.org/abs/2504.12522 · Jung et al. 2025, UI-Bench https://arxiv.org/abs/2508.20410 · Visual Aesthetic Benchmark 2026 https://arxiv.org/abs/2605.12684

Risks and homogenization: Goree et al. 2021 https://dl.acm.org/doi/10.1145/3411764.3445156 · Müller 2018 https://borism.medium.com/on-the-visual-weariness-of-the-web-8af1c969ce73 · Ström, same-ification https://mattstromawn.com/writing/sameification/ · Brunfaut, Blanding https://www.basedesign.com/opinions/blanding-branding-paradox · Google, Expressive design research https://design.google/library/expressive-material-design-google-research · DynamicSchemeVariant https://api.flutter.dev/flutter/material/DynamicSchemeVariant.html · Frost, recipes https://bradfrost.com/blog/post/design-system-components-recipes-and-snowflakes/ · Adobe, Spectrum 2 https://adobe.design/stories/design-for-scale/introducing-spectrum-2 · Davis on parametricism https://www.danieldavis.com/patrik-schumacher-parametricism/
