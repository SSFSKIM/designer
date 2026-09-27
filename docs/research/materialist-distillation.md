# Materialist: distillation notes

Law-by-law provenance for `skills/materialist/SKILL.md`, on the pattern of
`docs/research/personas/essentialist-distillation.md` and lighter. The runtime file carries one
provenance paragraph (§10); this file records, for every law, ban and check, which source it came
from and the passage or ledger section it rests on. A law with no source is marked **authoring
choice**, the way the essentialist record marks its tiebreaker, so a reader can tell a rule Apple
stated from a rule this skill decided. Recorded 2026-09-26.

## Sources

| key | where |
|---|---|
| `memo` | `docs/research/2026-09-10-liquid-glass-design-language.md`: Apple's HIG pages and WWDC25 sessions 219, 356, 323, 284, 220, read and quoted; §11 marks the practitioner critique secondary |
| `ledger §n` | `docs/doperpowers/specs/c9a-fidelity-claims.md`, by section, as `skills/materialist/references/optics.md` cites them |
| `react`, `web` | `packages/react/README.md`, `packages/platform-web/README.md`: the runtime's own contracts |
| `demo` | `apps/demo/DESIGN.md`: the user's daylight ruling (§0, 2026-09-03) and the site's glass law (§8, §9) |
| `2.3 spec` | `docs/doperpowers/specs/2026-09-10-liquid-glass-into-the-skill.md`: the curvature ruling (Decision Log, 2026-09-10) |
| `brief` | `docs/doperpowers/specs/2026-09-26-materialist-skill.md` Purpose: the user's statement of the register |
| `ive` | `docs/research/personas/essentialist/ive-interviews.md`, `ive-apple-cases.md` |
| `secondary` | STRV (ghost glass), Six Colors (Tahoe toolbars), NN/g (legibility), Louie Mantia (one material), as collected in `memo` §11 |

## §1 What the material is (character, plus the one law it states)

| Sentence | Source | Grounding |
|---|---|---|
| A lens, not a blur preset; edge refracts inward, more on a wider surface | ledger §5.113 | the rim band is a clamped linear function of span; the lens section of the demo's laws page |
| Body takes the backdrop's tone; over dark content it stays present, its level following the backdrop's | ledger §5.8, §5.153 §2, §5.179 to §5.180 | the body matches Apple's own reading over black at span 44 (132/133 light, 32/20 dark codes, a mid-grey plate on the light material); on 27 "Apple's material does not disappear anywhere on this bed", thin and thick 0.024 apart at the dark anchor against 0.48 on 26.5 (corrected at the 2026-09-26 review: the first draft described 26.5's size-gated vanishing as the default) |
| Body carries the backdrop's hue on the GPU tier | ledger §5.164 | retention 0.282 light active, 0.336 dark active |
| Shadow outside the surface whose blur and depth grow with size | ledger §5.159, §5.168 | `σ(span) = 8.96 + max(−6.83, 0.1314 · (span − 96))` on the light document |
| Thins when small, thickens when large | ledger §5.7 | the size law, inert below 32 and saturated at 96; memo, WWDC25 284: "A larger size is more opaque. A smaller size is clearer" |
| Recedes on focus loss | ledger §5.128 to §5.130 | the inactive endpoint: rim collapses, hue disappears, shade survives |
| Lights from the touch point and compresses on a spring | memo, WWDC25 219; `packages/motion/src/tunables.ts` | "Starting right under your fingertips, the glow spreads throughout the element"; `pressCompressionScale: 0.015` |
| A distinct functional layer floating above content | memo, HIG Materials | "Liquid Glass forms a distinct functional layer for controls and navigation elements ... that floats above the content layer, establishing a clear visual hierarchy" |
| Never in the content layer | memo, HIG Materials | "Don't use Liquid Glass in the content layer." |

## §2 The register: whose sentence is whose

| Sentence or idea | Attribution |
|---|---|
| "refined futurism with skeuomorphism at its finest", "a physical glass instrument held over the page", active curvature, smooth physical motion | the user's brief (`brief`) |
| "The skeuomorphism of the early 2010s failed because it depicted"; linen, leather, bevels | this file's synthesis, with `ive-apple-cases.md`'s iOS 7 flattening case as context; not an Apple statement |
| "This material depicts nothing. It behaves." The optical-versus-ornamental distinction | synthesis, drawn from the ledger: each behaviour named is a measured law (§1 above) |
| "designing and making are inseparable" | Ive, `ive-interviews.md:94` |
| No brushed metal, leather, bevel, faux grain; the content plane is real content | recommended 2026-09-26 and ruled by the user 2026-09-27; the boundary is an **authoring choice** grounded in Ive's material honesty and the demo's "one texture at the root, never per component" (`demo` §3) |
| An instrument over a world; a heads-up display without the neon | synthesis |
| Content full-bleed, edge to edge, carrying the colour; controls small and monochrome | memo, HIG Layout ("extend to the edges of the display"); WWDC25 323 (monochrome bars); WWDC25 219 ("imbue color ... in the content layer") |
| Daylight is the distinctive register; dark is where glass is easy | the user's ruling, `demo` §0: "every verified competitor demo is dark, because dark is where glass is easy; the harder and unclaimed demonstration is daylight" |
| Capsules for single-row housings, concentric children, one thickness | the user's ruling, `2.3 spec` Decision Log 2026-09-10: "prefer capsules for single-row floating controls; retain generous rounded rectangles where multi-row content needs the space"; "much better with more curvature" |
| Materialise, morph, glow, compress, bounce; no idle motion | memo, WWDC25 219 and 323; the "no idle motion" reading is the memo's own inference ("Every motion Apple describes is a response to input, a state change, or an environmental change"), marked there as such |
| Honesty as part of the aesthetic: the runtime reports what drew; the fallback is the design | `web`, the honesty core (`GlassGroupState`, "choosing CSS is not a fault"); `demo` §8 ("zero dev-mode diagnostics is part of done"); framed as an aesthetic by synthesis |
| Tiebreaker: "more like glass ... less like a page wearing it" | **authoring choice**, per `skills/designer/references/guidelines-authoring.md`'s tiebreaker convention, filled with the quality this skill optimises for |

## §3 The decision function

| Question | Source | Grounding |
|---|---|---|
| Control or content? | memo, HIG Materials; WWDC25 219 | "Don't use Liquid Glass in the content layer"; the tableview "would ... muddy the hierarchy" |
| What is under it, does it have structure to bend? | secondary, STRV; `demo` §0 | "On a plain white or monochromatic background, the blur has nothing to render, and the glass becomes invisible"; the demo rejected an editorial ingredient as "a flat backdrop with nothing for a lens to bend" |
| Could a sheet of glass do this? | **authoring choice** | a test synthesised from the measured behaviours in §1; each "yes" names a ledger law, each "no" a 2.3 anti-pattern |
| Does it flow from where it was? | memo, WWDC25 219 | "morphs between the controls in each context ... a singular floating plane"; "Instead of fading, Liquid Glass objects materialize in and out" |
| Readable at the worst phase, both schemes, reduced, and with the glass removed? | memo, HIG Accessibility, HIG Color, Adopting Liquid Glass | 4.5:1 and 3:1; "make sure its default or resting state ... maintains clear legibility"; "test your app's custom elements ... with different configurations of these settings" |
| "Fewer surfaces, larger, calmer" | **authoring choice**, leaning on HIG Materials "Use Liquid Glass effects sparingly" and the size law (larger is more opaque, ledger §5.7) |

## §4 Laws

### The two layers and the floating inventory

| Law | Source | Grounding |
|---|---|---|
| Every glass surface is a control, navigation or a transient platter; the count is small | memo, HIG Materials; WWDC25 284 | "Limit these effects to the most important functional elements in your app" |
| Glass never on glass; on the control, not its container or inner views; fills, transparency, vibrancy on top | memo, WWDC25 219; WWDC25 356 | "Always avoid glass on glass ... use fills, transparency, and vibrancy for the top elements"; "apply the material directly to the control, not its inner views" |
| A toolbar is not a surface; the platter is its members' fields merging | `react` | "`GlassToolbar` is deliberately not a glass surface ... the platter you see is its members' fields merging" |
| The slider-knob exception, a fill on the web today | memo, HIG Materials and Adopting Liquid Glass (the knob "transforms into Liquid Glass during interaction"); `react` (`glass-inside-glass` fires in both directions) |
| Everything else declares its own surface model beneath | `skills/designer/references/material.md` ("a layered system, not a blend"); `demo` §0 | the beneath layer is the product's |

### The live plane

| Law | Source | Grounding |
|---|---|---|
| Backdrop designed with both spatial frequencies, the fine part painted into the plane | `demo` §3 and `apps/demo/src/site/StageBackdrop.tsx` | "a graticule drawn outside it would sit over the glass unbent" |
| Check the varied region, at every phase | secondary, STRV; `demo` §8 (contrast sampled "across several phases of the backdrop's drift") |
| Prefer a texture plane; on the DOM path the hint is an assertion the runtime trusts | `react` | "vitrea does not automatically pixel-analyse arbitrary DOM"; the demo measured 1.6:1 to 3.0:1 from a dishonest hint (`apps/demo/src/site/Stage.tsx`) |
| Content reaches the window's edges; a bar beside content is a page wearing the material | memo, HIG Layout; secondary, Six Colors | "backgrounds and full-screen artwork extend to the edges"; Finder's toolbars read as "flat light gray ovals" because content stops at the window's inner edge |
| The plane is viewport-fixed | `web` (the root is `position: fixed; inset: 0` by construction); `demo` §4 |

### Groups

| Law | Source | Grounding |
|---|---|---|
| One backdrop read, one variant, one tint seed; at most three groups per bar; never text beside icon | memo, WWDC25 323, HIG Toolbars; `react` | "glass can not sample other glass"; "aim for a maximum of three"; "the illusion of a single action"; tint-mixing and variant-mixing warnings |
| Merge or separate by spacing, decided per pair | memo, Applying Liquid Glass to custom views | "A spacing value on the container that's larger than the spacing of an interior HStack ... causes Liquid Glass effects to blend together at rest" |
| Two groups need the larger group's sampling padding, derived, never pinned | `web`, `react` | "at least the larger group's effective samplingPadding", 3σ of the blur actually drawn; `proxy-overlap-after-enforcement` |
| No overlap within a plane; across planes is the morph | `react` | "Two glass surfaces must not overlap within one plane ... Overlap across planes is the supported case" |

### Geometry and the size family

| Law | Source | Grounding |
|---|---|---|
| Three shape kinds; concentric shares a centre; radius falls toward zero away from the corner | memo, WWDC25 356; ConcentricRectangle | "Fixed shapes have a constant corner radius. Capsules use a radius that's half the height ... concentric shapes calculate their radius by subtracting padding from the parent's"; "shares a common center" |
| Pinched or flared corners are the failure signal | memo, WWDC25 356 | "Keep an eye out for corners that feel too pinched — or flared" |
| Capsules for single-row housings and floating buttons; concentric inner controls; generous platters | the user's ruling (`2.3 spec`); memo, WWDC25 323 ("Bordered buttons now have a capsule shape by default") | the extension of the capsule across the floating layer is the user's, not Apple's, and SKILL.md §2 says so |
| Name the concentric anchor | memo, WWDC25 356, Adopting Liquid Glass ("nest perfectly into the rounded corners of windows"); the web anchor is an **authoring choice** the 2.3 draft made and this file keeps |
| A size family straddling 32 to 96, one radius per span, one thickness | ledger §5.7; `demo` §4 and `Stage.tsx` (112 / 68 / 40, thickness 8) | the law is exactly inert below `sizeSpanMin` 32 |
| Thickness 8 unless the product gives a reason | `web` (`thickness` default 8, `lensThicknessReference` 8) |

### Colour

| Law | Source | Grounding |
|---|---|---|
| Glass has no colour of its own; controls monochrome; colour in the content plane | memo, HIG Color; WWDC25 323; WWDC25 219 | "no inherent color, and instead takes on colors from the content directly behind it"; "The monochrome palette reduces visual noise" |
| One tinted control per view, primary action or status, on the background; a seed not a fill | memo, HIG Color; WWDC25 219 | "apply color to the background rather than to symbols or text ... Refrain from adding color to the background of multiple controls"; "When every element is tinted, nothing stands out"; a solid fill "breaks the visual character" |
| One seed per group | `react` | `tint-mixing`: the GPU tier draws the group in the first surface's colour |
| Label colour must not approach the content behind it; withholding the tint is legitimate | memo, HIG Toolbars ("Avoid applying a similar color to toolbar item labels and content layer backgrounds"); the withholding clause is the music-player demo's derivation, `references/examples.md` |
| Light and dark are separate measurements; hint and scheme differ | ledger §5.151 to §5.153 (per-scheme fits); `react` ("A backdrop hint and the colour scheme are different things") |

### Type and content on glass

| Law | Source | Grounding |
|---|---|---|
| One short line or a label; the material never carries information | `demo` §8 | "No prose over glass ... The material never carries information" |
| Ink is vibrant and automatic; four levels; a pick, not a ratio; measure on pixels | memo, WWDC25 323 ("a vibrant text color that adapts"); ledger §5.140; `react` (the four tokens and what each promises); `demo` §8 (axe "incomplete" over a canvas) |
| 4.5:1 and 3:1 in both schemes | memo, HIG Accessibility |
| Regular through bold; a symbol where one exists, a word where none does | memo, HIG Typography ("avoid Ultralight, Thin, and Light"); HIG Toolbars; WWDC25 356 ("a text label is always the better choice") |
| `color-scheme` on app content inside a plane | `demo` §1 | the CSS tier writes `light-dark(...)`, resolved against the element's own scheme |

### Motion

| Law | Source | Grounding |
|---|---|---|
| Materialise, never fade; morph; emerge from the control; no cross-fade | memo, WWDC25 219, 284, 323 | "materialize in and out by gradually modulating the light bending and lensing"; "prefer setting the effect property over the alpha"; "the bubble simply pops open ... right where you just tapped" |
| Glow and compression at the pointer, a bounce on release, never a colour swap | memo, WWDC25 219 and 323 ("scaling, bouncing, and shimmering"); `tunables.ts` (press 260 ms, ζ 0.72, scale 0.015) |
| No idle motion | memo §7's inference; `demo` §7 ("no parallax, no reveal-on-scroll, no drifting gradient, no animated blur") |
| Spring character; interruptible; Reduce Motion removes the elastic term | `tunables.ts` and the design spec's motion table; memo, WWDC25 219 ("disables any elastic properties") |

### Poses, schemes and variants

| Law | Source | Grounding |
|---|---|---|
| The receded pose is a designed state; never hand-animate it | memo, WWDC25 219 ("visually recedes"); `web` (`windowActivation: "auto"`, "its tint keeps its shade and loses its chroma"); ledger §5.168 §4 (no receded shadow) |
| Two variants, never mixed; clear only under Apple's three conditions with its dimming layer | memo, WWDC25 219; HIG Materials (35 %) | "They should never be mixed"; the three conditions as stated in 219 |

### Accessibility and the fallback

| Law | Source | Grounding |
|---|---|---|
| The four settings modify the material; design with all four open; where Reduce Transparency cannot be queried the app offers the setting and passes a boolean | memo, WWDC25 219, Adopting Liquid Glass; `core/src/accessibility.ts:283-296` (`"system"` and absence resolve identically; the `reduced-transparency-undetectable` diagnostic asks for "an explicit boolean"). Corrected at the 2026-09-26 review: the first draft said to set the overrides "explicitly to follow the system", which is the default and changes nothing |
| The CSS tier is the same material without refraction and a complete design | `web` (`css-tier.ts` doctrine, "the fallback is the design"); ledger §3.1 (tier coherence) |
| Labels real DOM; portalled content needs a landmark | `react` ("A `GlassButton` renders a real `<button>`"; "Portalling costs a landmark") |

### Layout under floating chrome

| Law | Source | Grounding |
|---|---|---|
| Inset derived from the bar's measured size; at rest no content under glass | memo, HIG Layout (safe areas); WWDC25 219 ("In steady states ... avoid intersections between content and Liquid Glass"); the measured-inset form is the 2.3 draft's web translation |
| Scroll edge where content passes under a control and nowhere else; on the scroll container, never an ancestor of the root | memo, HIG Layout, HIG Scroll views ("Scroll edge effects aren't decorative"), WWDC25 356; `web` (backdrop-root triggers demote with `probe-failed`) |
| No custom background, border or scrim under a bar | memo, Adopting Liquid Glass ("Reduce your use of custom backgrounds in controls and navigation elements") |

### The macOS reading (reference, not law)

Every item is Apple's, from `memo` §6 and §10: HIG Search fields, HIG Menus, HIG Tab bars, WWDC25
356 (hard and soft scroll edges, window-corner concentricity), HIG Windows (leading toolbar items
and window controls). Demoting them from law to reading is the authority decision recommended to the
user on 2026-09-26, recorded in the initiative spec's Decision Log, and ruled as recommended on
2026-09-27.

## §5 and §6: the home system and the derivation

The home system's rows are the runtime's defaults (`react`, `web`) plus three authored values: the
three-span family (the demo's sweep, one instantiation), thickness 8 (the runtime's default), and
"tint: none" (the memo's default state of glass, HIG Color). The derivation bullets rest on:
`skills/designer/references/material.md` and `effects-policy.md` for when glass is earned; the user's
daylight ruling; HIG Color and WWDC25 219 for the tint; WWDC25 219 for clear; WWDC25 356 for touch
versus dense desktop ("in dense desktop environments, they're best used for standout actions"); and
`references/vitrea.md` §9 for the path without vitrea. "The smallest honest version ... with the
tension recorded" is the designer skill's precedence rule, `material.md`, carried over.

## §7 Ban list

| Ban | Source |
|---|---|
| Glass on content | memo, HIG Materials; WWDC25 219 |
| Glass on glass; border, background, shadow or blur on a host | memo, WWDC25 219; `react` (host `background` is a solid fill; the rim and shadow are the material's) |
| Two variants; clear without dimming | memo, WWDC25 219; HIG Materials |
| Second tint hue in a group; tint on a label; solid fill; hand-rolled blur | `react` (`tint-mixing`); memo, HIG Color; WWDC25 219; WWDC25 284 (glass "is distinct from other visual effects, like UIBlurEffect") |
| Glass over a flat field | secondary, STRV and Six Colors; `demo` §0 |
| Cross-fade, opacity fade-in, idle motion, colour-swap press | memo, WWDC25 219, 284; `react` (opacity creates a backdrop root); memo §7 inference |
| Depicted material anywhere else | **authoring choice**, recommended 2026-09-26 and ruled by the user 2026-09-27; grounded in Ive's honesty line and `demo` §3 |
| Dishonest declaration; pinned padding; fixed inset | `react`, `web`; memo, HIG Layout (safe areas) |
| Prose on glass | `demo` §8 |

The mechanical subset restates these as checks a linter or a DOM walk can run; the ancestor trigger
list is `packages/platform-web/src/probe/backdrop-root.ts` (`filter`, `backdrop-filter`, `opacity`
below 1, `mask-image`, `clip-path`, `mix-blend-mode`), and "span at or above 32" is ledger §5.7.

## §8 QA lens

| Check | Source |
|---|---|
| 1 to 3, `[layer]` | memo, HIG Materials; WWDC25 219; WWDC25 284 (the 2.3 draft's rules 1 to 3, unchanged) |
| 4, 5, `[material]` variant, tint, fill, blur | memo, WWDC25 219; HIG Materials; HIG Color; WWDC25 284 (rules 4 to 7) |
| 6, `[material]` flat field | secondary, STRV; Six Colors (rule 16) |
| 7, `[material]` no depicted material | **authoring choice**, new; see §7 |
| 8, 9, 10, `[geometry]` | memo, WWDC25 356; ConcentricRectangle (rules 8, 9); the user's ruling (9); ledger §5.7 (10, new) |
| 11, `[grouping]` | memo, HIG Toolbars; WWDC25 356; Applying Liquid Glass to custom views (rules 11 to 14 folded into one) |
| 12, `[legibility]` contrast on pixels | memo, HIG Accessibility (rule 18); `demo` §8 for the measurement method |
| 13, `[legibility]` rest state and scroll edge | memo, WWDC25 219; HIG Scroll views (rules 15, 17); the hard/soft style clause dropped, see below |
| 14, `[legibility]` the four settings and the receded pose | memo, WWDC25 219; Adopting Liquid Glass (rule 19); the pose is `web` |
| 15, 16, `[layout]` | memo, HIG Layout; Adopting Liquid Glass (rules 20 to 22, with safe-area insets translated to a measured inset) |
| 17, `[motion]` | memo, WWDC25 219, 323 (rule 23) |
| 18, `[colour]` | memo, WWDC25 323, 219; HIG Toolbars (rules 24, 25) |
| 19, `[honesty]` | `react`, `web`, `demo` §8 and §9 (new: the hint audit, the resolved state, zero diagnostics) |
| 20, `[eye]` | `CLAUDE.md`'s fidelity discipline ("put the capture next to the native fixture ... and look"); new |

## Considered and not shipped

- **The slider-knob lift as an executable law.** Apple's one exception to the content-layer rule
  (HIG Materials; Adopting Liquid Glass). vitrea's layer model raises `glass-inside-glass` in both
  directions and across planes, so a knob on a glass bar has no expression in v1. Recorded in §4 as
  the exception and its web status, not as an instruction to build it.
- **iOS-only chrome rules.** Bottom-anchored search "if there's room", the trailing search tab, the
  floating tab bar that minimises on scroll and its accessory view (HIG Search fields, HIG Tab bars,
  WWDC25 356). Touch-platform conventions for a skill whose pages are web surfaces; dropped, and the
  desktop search placement moved to the macOS reading.
- **The 2.3 draft's rule 10, desktop half.** "Small, dense desktop controls are rounded rectangles"
  (WWDC25 356 on Mini, Small and Medium). The user's ruling extends the capsule across the floating
  layer's housings; the desktop half survives only as a derivation note about compact inner controls
  inside a capsule housing, which is the reconciliation the 2.3 draft's own QA glossary reached.
- **Hard versus soft scroll-edge styles, never mixed (rule 15's second clause).** The web has no
  primitive for either and a page builds one mask; the style taxonomy belongs to the platform and is
  kept in the macOS reading. One scroll edge per view, where content passes under a control, stays.
- **The background extension effect (rule 21's second clause).** Apple's mirror-and-blur under a
  sidebar (Adopting Liquid Glass). Hand-built on the web with no vitrea primitive and no measurement;
  the law kept is the one it serves, content reaching the window's edges. Recorded as a gap a page
  writes down rather than a rule it passes.
- **Safe-area insets as the mechanism.** `env(safe-area-inset-*)` resolves to zero on desktop; the
  2.3 draft's translation to an inset measured from the bar's box is what SKILL.md carries.
- **"Glass recedes on focus loss, which a page should not hand-animate" as stated in 2.3 §8.** The
  premise moved: since 0.18.0 the root follows `document.hasFocus()` under `windowActivation:
  "auto"`, so the law became "leave it on and design the receded state".
- **Leading toolbar items clearing window controls; the title bar as drag surface** (HIG Windows).
  No web equivalent; named in the macOS reading as not simulated.
- **Menu icons on the leading edge, all items or none** (HIG Menus). A platform menu convention;
  macOS reading only.
- **App icon layering rules** (WWDC25 220; HIG App icons). Outside a web page's scope.
- **Numeric merge thresholds, bar heights, radius values.** Apple publishes none deliberately
  (ConcentricRectangle exists "without hard-coded values"); nothing was invented. The demo's
  112 / 68 / 40 and radii 26 / 18 / 12 appear only as one instantiation.
- **Spring constants as law.** `tunables.ts` is advisory and unmeasured against a native frame
  sequence; SKILL.md states the character and `references/vitrea.md` the numbers, neither as a bound.
- **The macOS text-style ladder** (HIG Typography's 13 pt body and so on). Platform metrics for a
  platform's chrome; a web product's type is its own. The weight rule was kept, the sizes were not.
- **The widely quoted 1.5:1 contrast figure.** Unreproducible (memo §11); Apple's 4.5:1 and 3:1 are
  the floor used.
- **Increase Contrast alone with the body's hue retention.** Unmeasured (ledger, tracker); named as a
  gap in `references/optics.md` §16 rather than legislated.

## Added after the prior-art report (2026-09-26, later)

`docs/research/2026-09-26-liquid-glass-aesthetic-prior-art.md` (key `prior-art`) landed after the
first distillation and these sentences were added to `SKILL.md` on it. Its quotes came through a
fetch-and-extract tool; the report says to check any of them against the source before quoting
word for word, and the runtime file quotes only short phrases.

| Sentence or idea | Where in SKILL.md | Source | Grounding |
|---|---|---|---|
| "a new digital meta-material that dynamically bends and shapes light"; lensing as the primary way it defines itself; "to remain visually clear, deferring to the content underneath" | §1 | prior-art §1.1, WWDC25 219 | Apple's own definition of the material and its goal |
| de With: "we've come back, in a sense, to skeuomorphic interfaces, but this time not with a lacquer resembling a material" | §2 skeuomorphism | prior-art §4, Lux 2025-06-03 | practitioner statement of the register the brief names; secondary |
| Kamushken: "where glassmorphism blurs the background, liquid glass bends it"; "depth always comes back, but only the honest versions stay" | §2 skeuomorphism | prior-art §4, Setproduct 2026-06-09 | secondary; the bend versus blur distinction is the same as the ledger's `refraction` axis |
| Apple's lineage: Aqua, the real-time blurs of iOS 7, iPhone X, the Dynamic Island, visionOS | §2 futurism | prior-art §4, WWDC25 219 | Apple-stated |
| iOS 7's deference test: is the interface calling attention to itself, does it compete with content | §2 futurism | prior-art §4, Apple 2013 Tech Talk (Mike Stern) via the nonstrict.eu index | Apple-stated, second-hand transcript |
| "support interaction where needed, and remain unobtrusive when it's not" | §2 futurism | prior-art §1.2, WWDC25 356 | Apple-stated |
| Where the identity lives: Gruber's "see-through blandness"; identity in the plane, type, motion quality and one accent | §2 | prior-art §3.6 (Gruber, 2026-09) for the charge; the answer is **authoring choice**, aligned with WWDC26 251 ("the content layer is the best opportunity to express your brand identity") | contested item 25 of the report, resolved here as a law |
| "the visuals and motion of Liquid Glass were designed as one"; "an inherent gel-like flexibility" that "moves in tandem with your interaction" | §2 motion | prior-art §5, WWDC25 219 | Apple-stated |
| Motion held back where interactions are frequent; delight becomes distraction on repetition | §2 motion, §4 motion | prior-art §5, HIG Motion ("generally avoid adding motion to UI interactions that occur frequently"); NN/g and Moren for the repetition observation | Apple-stated, reinforced by critics |
| Springs start with no bounce; overshoot rewards momentum; the click bounce, "a little goes a long way" | §4 motion | prior-art §5, WWDC18 803, WWDC23 10158, WWDC26 289 | Apple-stated |
| Motion rationed by frequency; a page adds none of its own on top of the runtime's; Apple scales emphasis by input and the runtime does not yet | §4 motion | prior-art §5, HIG Motion; `packages/motion/src/tunables.ts` (one press response for every input) | Apple-stated for the principle; the runtime's gap is recorded in the spec's Deferred list (2026-09-26 review) |
| Legibility before translucency; the critics' central charge; regular glass wherever text sits | §4 type | prior-art §3.1 (NN/g, Fast Company, Heer, Arment); HIG Materials for regular over text | the charge is secondary; the law restates Apple's regular-variant rule |
| Design the opaque page first | §4 type, §6 | prior-art §4 (Kamushken, "Always design the solid-color version first"); the demo's own fallback doctrine (`css-tier.ts` header, "the fallback is the design") | secondary plus the runtime's contract |
| macOS 27 refinements: edge-to-edge sidebars, uniform toolbar, tighter window corners, menu icons hidden, improved diffusion, darkened edge with brighter highlights; the automatic scroll-edge style preferred | §4 macOS reading | prior-art §1.9 (WWDC26 102), §1.6 (HIG Scroll views, June 2026) | Apple-stated; supersedes the 2.3 draft's "menus carry leading-edge icons on macOS now" |
| Dense pointer-driven multi-window work wants more structure and opacity | §4 macOS reading | prior-art principle 23; Heer, Thomson, Gruber on the Mac | practitioner consensus, partly conceded by Apple's 27 changes |
| Apple's 27 description of the edge, "a darkened edge along with brighter specular highlights", beside W35's reading | `references/optics.md` §6 | prior-art §1.9 | Apple-stated; corroborates ledger §5.177 to §5.183 |

Not shipped from the report: the eight HIG design principles of June 2026 (Purpose, Agency,
Responsibility, Familiarity, Flexibility, Simplicity, Craft, Delight), which are a platform's design
philosophy rather than the material's; the contested floating inset chrome and self-minimising tab
bars, which stay a macOS and iOS reading; Federighi's and Dye's interview lines, which the report
could not fetch from source.

## Corrected after the proof (2026-09-27, 1.0.1)

Six fresh makers built the six briefs under the skill alone
(`docs/doperpowers/specs/2026-09-27-materialist-proof.md`, A), and six source readings of those
pages (`docs/research/data/2026-09-27-materialist-proof/review/<slug>.md`, each file's "What the
skill did not carry") found the skill teaching against itself. Each change names the reading that
motivated it and the source it was checked against before it was written; `review/x (n)` is item n
of that list in that file.

| Change | Where | Motivated by | Checked against |
|---|---|---|---|
| A platter holds choices and actions; a collection or table read in place is content even inside a dialog; floating is a placement, not a material. The queue, the alerts list, the vehicle's dossier and the forecast become opaque panels with their controls on glass | SKILL §3 step 1, check 1; `examples.md` music-player, transit-ops, park-trails, common ground, header | review/music-player (1), transit-ops (1), park-trails (3); transit-ops finding 2 | SKILL's own layer law (memo, HIG Materials); the 2.3 panel failed r1 on the same queue |
| A declared level is an override on both tiers and describes the displayed composite under the group's actual boxes at every phase; a texture group reads its own pixels on both tiers, one whole-source tone in the active pose and each surface's silhouette in the receded one; `analysis` names the sampling path | SKILL live plane, check 19; `vitrea.md` §2; `optics.md` §4; `examples.md` every Groups paragraph, template | review/music-player (2), transit-ops (2), park-trails (1, 2), photo-review (3, 4), film-festival (1, 2), product-launch (1) | `platform-web/src/root.ts:2140–2222` (declared hint first, both tiers) and `2438–2452`; `renderer-webgpu/src/renderer.ts:1038–1059` (local tone suppressed under a hint); `root.ts:1384–1425`, `backdrop-tone.ts:147, 191–250` (a CSS-tier root reads the supplied texture, whole source, 250 ms for a canvas or video); `test/silhouette-root.test.ts` (12 pass); ledger "One local reference through the solve" (active documents `source`, receded `silhouette`); `core/src/capability.ts:339–340` |
| A moved same-sized host keeps its cached box; the content box is what is observed; `invalidateGeometry()` through `onHost` is the route, absent on `GlassSegmentedControl` | `vitrea.md` §4 | review/transit-ops (3, 4), product-launch (2); the fix wave's content-box finding | `geometry-sync.ts:8–24, 164–185, 260`; `root.ts:3588–3589`; `react/src/surface.tsx:167–168`; `controls/button.tsx:60–74`; `controls/segmented-control.tsx:72–93, 262–273`; `css-tier.ts:1519, 1830` |
| An open morph host is not interactive and the app presses it through its channels after the morph's own glow write; the closed size is measured once and the open box at opening; `placement` avoids nothing; lifecycle, `container` and focus order are the app's; transient hosts keep a real box; the Reduce Motion collapse and its interim | `vitrea.md` §6; `examples.md` photo-review, transit-ops, park-trails, film-festival | review/music-player (3, 4), photo-review (2, 3), transit-ops (5), park-trails (4, 5), film-festival (3, 5), product-launch (3) | `react/src/morph.tsx:247–253, 421–450, 470–501, 620–641, 1111–1142`; `interaction.ts:94–98, 177–185`; `platform-web/src/channels.ts:119–145`, `root.ts:2420` (channels read whatever `interactive` says); `react/src/root.tsx:154–155, 404–410`; the photo-review fix wave's `press.ts`, verified on both tiers; `tech-debt-tracker.md`, the two materialist-proof entries |
| A capsule is half the measured span; a morph's closed end takes only `radius` | SKILL geometry, check 9; `vitrea.md` §4; `examples.md` photo-review | review/photo-review (5) | `geometry/src/corner.ts:40–42, 84–94`; `react/src/surface.tsx:341–357`; `morph.tsx:110–134` |
| A custom `GlassSurface` is not interactive by default | `vitrea.md` §6 | review/product-launch (4) | `react/src/surface.tsx:199` |
| A plane the page chooses is chosen or reframed for structure; content shown as it is may go flat in phases the record lists; the rest-state law is about reading content; the scroll edge is one of two compositions and a straddling surface describes the composite | SKILL live plane, layout, checks 6, 13; `examples.md` photo-review, film-festival, park-trails | review/photo-review (1, 6) and the session's ruling on its finding 1; park-trails (2); film-festival (2); product-launch finding 1 | **authoring choice**, on the session's ruling; HIG Materials for content under controls |
| The resolved policy covers the material; authored marks are checked after forced-colour substitution; page motion follows Reduce Motion as it changes; the segmented indicator's selection and positioned track are the app's | SKILL accessibility, check 14; `vitrea.md` §4 | review/music-player (5), product-launch (5), film-festival (4); park-trails, transit-ops and product-launch check 14 | `controls/segmented-control.tsx:251–289` |
| Contrast evidence is per label, phase, scheme and pose, and a miss is a failure | check 12; template | review/photo-review (7); film-festival check 12 | none needed: a recording rule |
| `quaternary-ink-on-thin-material` is page-scoped | `vitrea.md` §1; check 19 | review/film-festival (6) | `platform-web/src/root.ts:1110–1133, 3074–3076`; `ink-stylesheet.ts:139–170` |
| The dark scheme is a second material to design and measure; pinning the scheme is not the answer | SKILL poses and schemes | the eval, `docs/research/data/2026-09-27-materialist-proof/eval/results.md` "Reading", finding (2) | the same file: camera page 51/51 light and 36/51 dark, weather page 88/88 and 71/88 |

An independent review of this correction found seven places where it contradicted itself or the
runtime, and each was closed in the same version: a Reduce Motion remount must happen with the morph
closed (`morph.tsx:421–430, 620–621`); the press write wins only when its listener subscribes after
the React ticker's (`root.ts:3265–3281`, `react/src/root.tsx:385–390`, `press.ts:179–181`); a fixed
radius is clamped, so a capsule fails by growth, not by any change (`corner.ts:90–94`); "floats" became
"are glass", and the background prohibition and check 16 are scoped to glass hosts; step 2 and the
flat-field ban carry the page-chosen versus shown-as-is distinction; film-festival's no-hint choice
is conditional on the footprint comparison and its menu re-measures; the permit platter's boundary
matches §3's.

Not shipped from the readings: the fix wave's brief offered a second route for a texture group,
declaring a hint only where the group resolves the CSS tier, on the premise that that tier has no
pixels. It reads them (W7, `root.ts:1384–1425`), so the route was replaced by "declare nothing where
the source's overall level holds". The audit's document scroll (park-trails (6)) and the stale
Increase Contrast line in a demo record (park-trails (7)) belong to the instrument and the demo, not
the skill. The four runtime gaps stay in `tech-debt-tracker.md`; the skill states the contract and
the interim route for each.
