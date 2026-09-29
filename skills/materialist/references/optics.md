# What the material is: the optics, measured

Read this to reason about a composition you have not seen before. The aesthetic in `SKILL.md`
follows from what the glass physically does, and an agent that knows the physics can predict how a
page will read without a rule for every case. The statements below are measurements of Apple's own
material, taken by the calibration harness in `packages/calibration` against native captures and
shipped in vitrea as fitted laws, wherever the ledger says so; where a number is a designed default
rather than a measurement, the tint's appearance in §11 and the motion's timing in §14, the section
says so. The default material is macOS 27's; the frozen macOS 26.5 material is named where the two
differ. The section numbers in parentheses are the fidelity ledger,
`docs/doperpowers/specs/c9a-fidelity-claims.md`, for anyone who wants the evidence.

Two framing facts first. The material is a **lens**, not a blur preset: a real-time, size-dependent
optical object with thickness, a rim that bends what is behind it, a body that takes the tone and
the hue of its backdrop, and an exterior shadow that scales with the surface. It is measured as a **macOS controls
material**, not visionOS window glass; the spatial register borrows Apple's composition while naming
the unmeasured reach of these laws at window scale below.

## 1. A sheet with thickness

Every surface has a thickness, 8 CSS px by default, and that number is the reference the lens is
scaled from rather than a free knob. The edge of the body refracts the backdrop inward: a rim band
whose displacement is a clamped linear function of the surface's shorter span, so a wider surface
bends more and a narrower one less. The bend follows the surface's own field normal, so it is
strongest along the straight sides and turns through the corners; past a knee around span 64 to 72
it blends toward the gradient of the inscribed oval, which is what makes a large plate read as a
single lens rather than a bevelled frame (§5.113, the laws page's lens section).

**Consequence.** Refraction is visible only where the backdrop has edges, gradients or texture for
the rim to displace. Over a flat field the lens has nothing to bend and the surface is a translucent
panel wearing a physics costume. Designing the backdrop is designing the material.

## 2. The size law

One smoothstep on `span = min(width, height)`, from 32 to 96 CSS px, drives the thickness-derived
facets at once: lens depth, occlusion (how opaque the body is) and the inner shadow. Below span 32
the law is **exactly inert**: a control at 28 px renders as if the law did not exist. At 96 and above
those facets saturate (§5.7, §5.113). Two things keep growing past 96 on their own laws: the body's
heavy scatter share rides a ramp that runs to span 256 (§3), and the exterior shadow's blur grows with the caster while its
amplitude grows to span 160 and holds there (§7).

| span (CSS px) | what the eye reads |
|---|---|
| under 32 | a thin, clear sheet; no size behaviour at all |
| 40 | the thinnest glass that shows the law: light haze, shallow lens |
| 68 | mid-curve: visible depth, the backdrop softening but structured |
| 96 and above | the thickness facets saturate: the most opaque body the material draws; the haze and the shadow keep deepening |

**Consequence.** A size family has to straddle the band for the material to show its size behaviour:
a set of controls all at 28 to 30 px demonstrates nothing, and past 96 what still changes with size is
the haze and the shadow, not the body's depth. Apple's phrasing, "A larger size is more opaque. A smaller size is clearer"
(WWDC25 284), is this law. It also means that legibility is protected by size: a large panel
behind text hazes its backdrop more than a small button does, so text on a large surface is the safer
case and text on a small one the harder.

## 3. Two components in the body

The interior is not one Gaussian blur. A sharp component keeps the structure of the content behind
the glass, and a heavy scatter component deepens with span and with the pixel's own depth under the
surface, on a ramp of its own that runs to span 256 rather than the size law's 96. On the WebGPU tier
the two are mixed per pixel; on the CSS tier one `backdrop-filter` carries their area average for the
box (§5.113, §5.121). The heavy component's width is a fitted leaf per document: 14 device px at 1x
and 20 at 2x on the macOS 27 light document, 0 on the dark one, and 9 on both scales for the frozen
macOS 26.5 material (§5.122).

**Consequence.** Text behind a small control stays legible through it, and the haze over a large
plate is genuine depth rather than a fog applied to it. Do not add your own blur to "help".

## 4. The body takes the tone of the backdrop

The interior's level follows the backdrop's level along a measured four-anchor curve that varies a
little with thickness, and below an encoded input of 0.003 a separate branch takes over so that the
body reads what Apple's does over black: on the light material a quiet mid-grey plate, on the dark
material near-black. That is the measurement the codes record: at span 44 the four macOS 27 endpoints
match Apple's own reading over black exactly, 132 and 133 codes on the light material, active and
receded, 32 and 20 on the dark (§5.8, §5.179 to §5.180). On macOS 26.5 the response was size-gated
the other way: a small surface over a near-black backdrop took that backdrop's tone and vanished into
it while a large one kept its own appearance. macOS 27 removed that flip; Apple's material no longer
disappears anywhere on the bed, and thin and thick differ by 0.024 at the dark anchor where 26.5
differed by 0.48 (§5.153 §2). The table is the light active document's anchors.

| backdrop, encoded | light material's thin body | thick body |
|---|---|---|
| 0.11 | 0.28 | 0.31 |
| 0.425 | 0.54 | 0.56 |
| 0.95 | 0.94 | 0.96 |

**Consequence.** Over dark content the material stays present on both sizes, a lighter plate than
its backdrop rather than a vanishing one, and the small-surface light/dark flip
with the backdrop describes the macOS 26.5 material, not the default one. The
body still has to be told what it sits over: on the DOM path the group's declared tone and luminance
is what it adapts to, and a false declaration measurably breaks label contrast. On the texture path
the runtime reads the pixels itself, unless a declaration overrides them, which it does on either
tier (`references/vitrea.md` §2).

## 5. The body carries the backdrop's hue, on the WebGPU tier

After the body composites over the blurred backdrop, its chromaticity is restored toward the
backdrop's by a fitted fraction, at a held luminance: 0.282 on the light active material and 0.349
receded, 0.336 on the dark active material and 0.142 receded. Over an achromatic backdrop the
retention is exactly the identity (§5.164). Apple's material keeps 0.71 to 0.83 of the backdrop's
chroma in the light scheme and 0.90 to 0.97 in the dark. Before this leaf vitrea's light material
kept a quarter to a third; after it the body keeps 0.51 to 0.57 on a focused light window and 0.35 to
0.37 on a focused dark one (§5.165 §9), so the glass now carries most of the picture's colour and
still less of it than Apple's does. The remainder is a named gap (§16).

**Consequence.** Over a photograph, a gradient or artwork the glass reads as the picture's own
colour seen through a lens, not as a grey plate of about the right lightness. The CSS tier carries
none of this, measured and declined on both schemes, and Reduce Transparency stands it down, so a
composition must never depend on the hue for meaning. Colour is the content plane's; the glass shows
it rather than owning it.

## 6. The rim, and what is still open

Apple's active material carries a one-CSS-px bright inner line at the edge, 24 to 53 codes above
the deep body, bright where the surface normal is vertical and faint where it is horizontal, and it
lifts the body's own saturated channels rather than adding white (§5.177). vitrea draws a lit edge
graded along a diagonal axis instead, and four waves of identification have shown the reference's
edge needs a colour-conditioned directional law that this bed cannot yet fit (§5.181 to §5.183).
In the receded pose the rim collapses on both materials. Apple's own description of the macOS 27
change names both sides of what the bed reads: a darkened edge and brighter specular highlights
(WWDC26 Platforms State of the Union). The bed reads a bright inner
line (§5.177) and a tight dark band just outside the contour (§5.159), and neither is closed.

**Consequence.** Never draw a border on a glass host; the rim is the material's own and a CSS
border sits on top of it as a second edge. And do not design a composition whose reading depends on
the edge's exact brightness: it is the one part of the material vitrea states as an open gap.

## 7. The exterior shadow, graded by the caster

The active material removes light from the plane outside the surface: a shadow displaced 7.95 CSS px
downward, grown by a small outset (0.50 px on the light material, 1.80 on the dark), and blurred by a
σ that is a line in the casting span above a knee,
`σ(span) = 8.96 + max(−6.83, 0.1314 · (span − 96))` on the light document (§5.159, §5.168). Its
amplitude grows with span as well: a thin control removes about 2 % of the light at its darkest;
a 160 px panel about 25 % on the light material and 34 % on the dark. Above 160 the
amplitude holds, rather than extrapolating: 0.2518 light and 0.3443 dark at span 500 too. The σ
column below is the light document's law, not a measurement at the window row.

| caster span | σ (CSS px) | CSS `box-shadow` blur |
|---|---|---|
| 44 | 2.1 | 4.3 |
| 96 | 9.0 | 17.9 |
| 160 | 17.4 | 34.7 |
| 500, window — extrapolated | 62.0 | 124.1 |

**Consequence.** A small control sits close to the plane and a large panel floats higher; the
difference is the material's statement of depth, and it is why a glass page needs no elevation
ladder of its own. The shadow's reach sets how far the material paints outside its surface; the gap
two sampling groups need is a different number, three σ of the body's blur, which the runtime
derives for a layout (`samplingPaddingFor`) and which also grows with the larger member. The shadow
is the material's, never a `box-shadow` token you write; and the **receded** material casts
none at all, because Apple's unfocused window was measured to remove no light from 3 CSS px outward
on every inactive cell (§5.168 §4).

## 8. Two poses

An unfocused window's glass recedes: on macOS 27 the body darkens and the rim collapses, a tint
keeps its shade and loses its chroma, and the exterior shadow stops (§5.128 to §5.130, §5.168). The
runtime follows the document's own focus by default (`windowActivation: "auto"`), swapping the posed
material in one frame on the WebGPU tier and fading the shadow out on the CSS tier.

**Consequence.** The receded pose is a state of your design, not an effect: look at the page with
the window unfocused. Do not hand-animate a recede, and expect the primary action's tint to survive
as an achromatic shade rather than as its colour.

## 9. Two schemes

The material is measured per colour scheme; the dark material is not the light one dimmed. A
scheme picks one endpoint of the selected document, and a group's backdrop hint is a different
statement: the hint says what is behind the surface, the scheme says what the surface is made of. A
dark page can honestly hand a light hint to a surface over a white card.

## 10. Two variants

`regular` is the answer for reading surfaces, save `SKILL.md` spatial condition 8's reading
exception, whose measured floor this file's constants do not guarantee. `clear` has a lower
nominal tint alpha (0.1)
against the calibrated regular body, but a different, uncalibrated blur (σ 4 against regular's
1.25). Its rim and specular constants are unfitted; it implements none of Apple's adaptive clear
contract. Core requires a dimming policy or falls back to regular, and resolves
`adaptation: "constrained"` with that policy; neither renderer reads the dimming or adaptation
fields. The policy alone paints nothing. `DEFAULT_CLEAR_DIMMING` is advisory
`{ scrim: 0.28, direction: "darken" }`, not calibration or an installed scrim. The page paints the
layer into its plane and measures the result. HIG Materials conditionally suggests **dark at 35%**
over bright content; the `Glass.clear` API example uses **black at 30%**. WWDC25 219 supplies the
three media/acceptable-dimming/bold-bright-foreground conditions, not a percentage. Never mix
variants on one page at once.

## 11. A tint is a shade of its seed

The tint is an opaque, hue-preserving shade of the seed colour whose brightness follows the untinted
material's own luminance under it, per pixel on the WebGPU tier and at one backdrop level on the CSS
tier, so one orange settles to a deep amber over dark content and to the seed itself over light
(§5.10, the laws page). The colour's alpha is the strength. A tint never moves the material's
occlusion, which is the axis the accessibility policies operate on, and the published ink follows the
tinted material. It carries no fidelity number: the appearance is designed, not calibrated.

**Consequence.** Colour on glass is one seed on one element, the primary action or a status, on the
control's background and never its label. When every element is tinted nothing stands out, and a
solid `background` in place of a tint is opaque and stops being the material.

## 12. The ink

Every host publishes four label levels through Apple's vibrancy operator, macOS's ladder rather than
iOS's: primary, secondary (holds WCAG 4.5 against the surface wherever the primary can), tertiary and
quaternary (no body-text floor). It is a two-pole pick against the material actually drawing, not a
contrast calculation, and it promises no ratio (§5.140).

**Consequence.** Contrast over glass is measured on rendered pixels across the backdrop's phases,
never assumed from a token, and a page that needs a guaranteed ratio sets its own ink on a child
element.

## 13. Accessibility settings are material states

Strictest preference wins. Reduce Transparency frosts harder, occludes more, caps refraction at the
rim-only bend and stands the hue retention down. Increase Contrast strengthens the border and pushes
foregrounds toward monochrome. Reduce Motion floors every spring at critical damping, shortens
morphs to seven tenths and steps presence. Forced colours removes the glass entirely and hands the
surface the platform's palette (§5.6, §5.141, §5.143).

**Consequence.** Each is a state to open and look at, not a degradation to apologise for; the
composition carries hierarchy in layout, grouping and type, so removing the material removes an
effect and never the structure.

## 14. The motion's character

Per-channel drivers, not springs everywhere. Geometry, morph and press compression ride
velocity-preserving interruptible springs, slightly underdamped so that a trace of overshoot reads as
material rather than as a tween. The lens strength is critically damped, because past 1 it visibly
over-bends. Press glow is a fast attack and a slow decay: light arrives with the finger and lingers
after it. Backdrop adaptation is a low-pass with hysteresis so scrolling past a contrast edge cannot
pump the body. Presence is a monotonic ease with no overshoot. The shipped constants are advisory
defaults in `packages/motion/src/tunables.ts`; nothing has yet been measured against a native frame
sequence.

**Consequence.** The glass has no idle motion. Everything it does answers input, a state change or
the environment: a press, a morph, a pose, a scroll edge. A release bounces; a materialise does not.

## 15. Two tiers, one material

The CSS tier holds no optical number of its own: it derives one `backdrop-filter` and one `rgba()`
layer, a `box-shadow` and a rim from the same profile document the WebGPU tier reads, so retuning
the material moves both (§3.1). What it cannot draw is stated by contract: `refraction: "none"`, no
hue retention, a rim that is one number rather than a field, and a `collapsed` body where the cost
budget cannot afford two layers. Choosing the CSS tier is not a fault, and a page that only ever
requested it resolves `health: "ok"`.

**Consequence.** The fallback is the design. Compose so that the CSS tier is the same page without
refraction, and look at it once as a matter of course.

## The material at window scale

The bed reaches span 160 CSS px: `rrect-lg` is 280 × 160 in
`apps/reference-apple/scenes.json`. The size law saturates at 96; the scatter ramp's top of 256
was fitted with that largest scene held out (`material.ts`, W11c G1, §5.41), not measured on a
256 px native window. At span 400–800 the runtime evaluates the same laws beyond their observed
size range. The body-depth gain has already saturated, scatter rises only to 256, shadow amplitude
holds its span-160 value and shadow σ keeps growing (§7's extrapolated row). A large window is
not an independently fitted thick material, and increasing its thickness is not a contrast proof.

The published-ink dead band is a property of the **drawn body**, not of the photograph behind it.
With the steady-state primary alphas from `vibrancy.ts`, neither pole reaches 4.5:1 on a neutral
surface between roughly encoded 0.393 and 0.490; secondary cannot exceed primary and tertiary and
quaternary have no reading floor. The source's average, the group's tone input and the surface
behind a line of text are three different quantities. A window over a graded source declares the
level measured under its own footprint when the whole-source average is not representative
(`vitrea.md` §2), then measures every rendered text line across phases, schemes and poses, with
the worst line gating. Grade the environment or author ink on a child; never falsify the hint to
force a pole. A calm average is not enough where individual lines cross structure (NN/g,
Glassmorphism, in the spatial memo §6.1).

On CSS, `CSS_TIER_TWO_LAYER_AREA_BUDGET_DEVICE_PX` is 400,000: the root sums width × height × dpr²
for all its **present CSS hosts**, counting area once per host, not once per filter layer. Above
that sum it collapses the heavy layer into one mixed-σ body. A lone 600 × 500 window costs 0.3 M
at dpr 1 (two-layer), 1.2 M at dpr 2 (collapsed). Read `cssBody` from `GlassGroupState` rather than
infer it from window size, record the actual form and inspect both; this is a compositor budget,
not a fitted optical threshold (`css-tier.ts`, `css-tier-layers.ts`, `root.ts`).

Clear does not remove these obligations. Its constants and its missing dimming implementation are
§10; a page-owned layer sits below its footprint in the sampled plane, never on the host, and
modal dimming is a separate attention treatment (WWDC25 356). Both clear optics and the dimming
choice remain uncalibrated. visionOS glass explicitly limits background information and adapts
without a distinct Dark Mode (HIG Materials); it is a different, unmeasured material here. The
spatial register is **Apple's macOS material composed in Apple's visionOS way** — Apple-shaped,
not visionOS fidelity. Put that statement in the page's record, not just its implementation notes.

## 16. The gaps, named

So that no composition is built on a fidelity that is not there: the inner edge line (§6 above),
the deep body's grey middle and its chroma on saturated backdrops (§5.180), the body's chroma
retention at 0.51 to 0.57 of the backdrop's in the light scheme and 0.35 to 0.37 in the dark against
Apple's 0.71 to 0.83 and 0.90 to 0.97 (§5.164, §5.165 §9), a rendered shadow σ still 1.3 to 2.8 CSS
px wider than Apple's fitted σ (§5.169), the CSS tier's residuals, and Increase Contrast alone with
the hue retention, which is unmeasured. The ledger records each with the work
that would close it. The spatial register adds window-scale extrapolation beyond span 160,
unmeasured visionOS glass, a published-ink dead band, CSS's area-dependent collapsed body, and
clear's uncalibrated optics, unread adaptation field and page-painted dimming layer. None is closed
by a composition that merely looks plausible. The eye is the last referee: when a page matters,
put its capture beside a native one and look.
