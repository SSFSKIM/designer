# The gallery's flagship: Tonight, a planetarium display in clear glass tuned toward a lens

Status: landed 2026-09-28; Outcomes and Retrospective at the tail. The independent review's findings and their disposition are in the Revision Notes.
Parents: `2026-09-26-materialist-skill.md` (the skill), `2026-09-27-materialist-proof.md` (the
instrument, the pass line, the six instrument pages), `2026-09-27-materialist-spatial-register.md`
(the second register and its two pages). Built in the main session by the session itself, on
vitrea 0.24.0 from workspace source, at `apps/demo/src/gallery/planetarium/`; its record is
`DESIGN.md` there; live at `https://ssfskim.github.io/designer/gallery/planetarium/` on the next
Pages deploy.

## Purpose

The user, 2026-09-28: "try making one design, in this main session, that will be like a flagship
demo for this vitrea liquid glass — using its full capability, full aesthetical potential, optics,
everything included; I would want to see more optical glass than frosted glasses." The day before,
the answer to whether the six demos' restraint was the library's limit or the skill's instruction
was: instruction, mostly, and the two real library facts were Apple's unmeasured clearer slider
position and no optics off the GPU tier. And the direction "liquid glass as a core material of
design, not like a sidecar".

The eight gallery pages read as frost, the two spatial pages included: the start page's own record
found that the shipped `clear` variant at window span drew the MORE frosted material, because the
size law multiplies its base blur by up to eight and the body's heavy scatter component rides to
span 256. Every page also ran the regular material's fitted tone response, which solves the body's
occlusion until it reaches Apple's measured level: over a dark plane the body becomes the plate
Apple's macOS controls material draws, and no base blur or tint alpha changes that (the sweep in
Surprises). So a flagship that shows the lens rather than the frost has to say, leaf by leaf, what
in the shipped material makes a window opaque, and stand exactly that down for the clear variant,
in the runtime's own tuning API, with the runtime reporting `tuned: true` and the record saying
why each leaf moved.

After this initiative: one page in the gallery whose environment is the real sky over a place,
drawn live, whose four glass surfaces transmit that sky and bend it at their rims, that runs the
runtime's whole surface — GPU texture path, thickness 14, morphs, press, materialise, the specular
sweep nobody had driven, the receded pose, both schemes, the CSS tier, the four accessibility
states — and that the same instrument as the eight pages read: zero diagnostics, zero ban findings,
every text line on glass measured per line in every state, the honesty core's readouts recorded.

## Design

### A. The product and the register

**Tonight**, a planetarium display: the real sky over a place at the page's time, turning with the
Earth, and what is up in it. Spatial register, named before the first host: the product's surfaces
are the interface (a guide beside the thing it describes; a display) and the world is their
environment. The person drags the sky to turn it, clicks a star or planet to read about it, scrubs
or plays the night, and chooses a place; the glass carries what they read.

### B. The environment: the sky itself, drawn

One viewport-fixed WebGL2 canvas, supplied to the runtime as a live canvas texture, painted every
frame the sky changes: a stereographic projection centred 36° up (conformal, so a constellation is
its own shape and the horizon is an arc), 84° of vertical field, a view the person pans. In it:

- 9,096 stars of the Yale Bright Star Catalogue (public domain) as additive point sprites sized
  and coloured by magnitude and B−V, 88 with proper names checked against the catalogue's Bayer
  designations at build time;
- NASA SVS's Deep Star Maps 2020 Milky Way layer (without bright stars) and its constellation
  figures layer, in J2000 celestial coordinates, sampled through the inverse projection;
- the Sun, Moon and five planets from astronomy-engine (MIT), the Moon a lit disc whose limb
  points at the Sun, both drawn at five times their angular size as a planetarium does;
- night airglow, twilight by the Sun's altitude, a blue day, a ridge line for the ground and a
  glow above it; labels for the bodies and the chosen star, and a ring on the chosen object;
- the clear variant's dimming layer, painted into this plane under each glass footprint (D).

It is real content: the sidereal turn is the page's idle, the time-lapse is the person's, nothing
is animated for the glass's sake. By day the sky goes nearly flat except the Sun's glow and the
horizon; that is content shown as it is, recorded as a phase.

### C. The material: clear, tuned toward a lens, with the reasons

Every group is `clear` at thickness 14 (the top of the register's stated range; the lens depth and
displacement scale with thickness over the reference 8, and the lens is what the page is for).
One tuning object, `MATERIAL_TUNE`, passed as `materialProfile`; the runtime reports `tuned: true`
for every group. Each leaf, and why (the sweep that found it is in Surprises):

| leaf | shipped | tuned | why |
|---|---|---|---|
| `optics.clear.blurSigma` | 4 | 0.6 | clear's base blur is nominal, not fitted; at 4 the size law draws a window body at σ 30–38 px |
| `optics.clear.tintAlpha` | 0.1 | 0.02 | a tenth of white over a night sky is a grey plate; a fiftieth is a sheen |
| `sizeScatterGainMax`, `…2x`, `…Far2x` | 8, 4.8, 4.8 | 1 | the heavy scatter component samples the pyramid's last level at window span, a flat field whatever the base σ; at gain 1 the heavy level is the sharp one |
| `sizeHeavyTapSigma`, `…2x` | 14, 20 (light) | 0 | the light document's second, wider blur, stood down with the heavy share |
| `sizeOcclusionGain` | 0.05 | 0 | the size law's occlusion facet: a twentieth of the neutral at window span, which on the light material is white over a night sky |
| `backdropToneResponseStrength`, `backdropToneBlackStrength` | 1 | 0 | the fitted response solves the body's alpha up to Apple's measured level, a plate; over black the light material's branch draws 132 codes; clear's adaptation is `constrained` by contract and read by neither tier, so the page stands it down and makes the dimming layer the adaptation |

Nothing else moves: the lens law, the rim, clear's specular and inner shadow, the exterior shadow,
the hue retention, the receded pose and every accessibility fold are the shipped material's. The
regular material is untouched by the page, which never draws it.

### D. Legibility: the dimming layer is the adaptation

Clear requires a dimming policy and neither tier paints one. The page paints it into the sky under
each host's footprint, and the strength is ADAPTIVE: the undimmed level under each host is measured
from an eighth-scale render of the same frame, the strength is set so the composite lands at or
below a target (linear 0.046, encoded about 0.24), floored at 0.16 and capped at 0.9; the
composite is then measured again and declared as the group's hint. At night the floor holds and
the sky shows through; by day the same window shades a blue sky to a level its white ink reads on.
The layer is feathered INWARD from the footprint's edge, so it is a vignette inside the rim and
never a halo outside it (the start page's clear comparison read the outward feather as a heavy
shadow). Re-measured on a cadence, on every layout change, and through the time-lapse.

Ink: the runtime's primary token on children; the secondary authored at 88 % of the primary (the
runtime's secondary was measured under its promise on window-scale bodies by both spatial makers);
tertiary only for hairlines; quaternary never named. Text stays 40 px off the window's side edges,
because the lens band at thickness 14 is 47 px deep and the displacement at 40 px in is under a
thousandth of its edge value.

### E. Windows and ornaments

One window (Tonight: place, the twilight state and its next change, the chosen object's card, the
list of what is up; 400 × 560, radius 28), one glance module (the Moon: phase glyph, illumination,
rise and set, the next quarter; 320 × 176, radius 28), two ornaments in the overlay plane, each a
`GlassMorph` from a 48 px capsule to a platter of radius 24: Place (seven places on two
hemispheres, the person's own location, the Reduce Transparency setting, the credit line) and Time
(an hour either way, play, and a Timeline platter with the night as a scrubber from noon to noon,
sunset and sunrise marked). The ornaments act on the whole scene, sky and window alike, so they hang
at the scene's top and bottom edges in the open sky between the window and the module, and their
platters open into sky, never over the window (the register's texture-path rule). The Time ornament
stays above the drawn ridge (the layout asks the projection where the ridge crosses under it).
Gap: the runtime's derived padding for this material, never less, with 32 px of air as the
design's floor. Concentric anchor: the window corner (28); the card inside is 28 − 8.

### F. Motion

Materialise on arrival (`present` flips once the sky's first frame is supplied), and as the
material arrives the page drives the runtime's specular sweep once around each rim — the `sweep`
and `shimmer` channels, which the highlight pass draws and no binding had ever driven — staggered
across the four hosts, on the runtime's frame loop, not under Reduce Motion, never at idle. The two
morphs are matched geometry. Press on the closed ornaments is the runtime's; inside an open platter
the page writes press, glow and the press point onto the platter's host from a frame subscription
taken when the press begins (the cookbook's recipe). The time-lapse and the sidereal turn are
content.

### G. Tier, poses, accessibility

`renderer="webgpu"`, `?tier=css` for the CSS tier (the same page without refraction; `cssBody`
recorded), `colorScheme="auto"`, `windowActivation="auto"`; the page's own Reduce Transparency
switch passed as a boolean; forced colours gives each host's full-size child a CanvasText frame on
the WebGPU tier (the tracked runtime gap) and every authored mark an outline.

### H. What is measured and what is not

Apple's macOS material composed in Apple's visionOS way, at spans beyond the bed (160), on the
clear variant no bed scene declares, with six of its leaves tuned by the page: Apple-shaped, not
Apple-measured, and the record says so beside every number. The nearest Apple surface is visionOS
window glass over a room; no native capture exists in the harness; no comparison was made.

### I. The instrument and the line

The proof's audit (`glass-audit.mjs`: seven passes, the spatial reads, the phases hook with four
instants of the pinned day — night, dusk, dawn, day — inner scrollers, the CSS tier, the receded
pose) at `?at=22:30` on the day of the run, plus an independent code review. The line: zero
diagnostics on both channels, zero ban findings on both lists, every text line on glass at or above
its floor in every state read, the four emulation passes clean, no glass drawn under forced
colours. No four-rater panel: that protocol reads pages other makers built from the skill alone,
and this one the session built itself; the user's eye is the referee it waits for.

## Decision Log

1. Decision: spatial register, named before the first host. Rationale: the product's surfaces are
   the interface and the sky is their environment; the direction was glass as the core material.
2. Decision: `clear`, tuned, rather than `regular` or shipped `clear`. Rationale: the ask was
   optical over frosted; the sweep (Surprises 1–3) showed that neither variant's base blur nor tint
   alpha decides whether a window transmits, and that three fitted laws of the regular material do;
   the tune names those and only those, in the runtime's tuning API, reported as `tuned`.
3. Decision: thickness 14 across the family. Rationale: the lens is the subject; 14 is the
   runtime's own open-morph thickness and the register's stated ceiling.
4. Decision: the dimming layer adaptive per host, inward-feathered. Rationale: D; the day phase
   needs 0.9 where the night needs 0.16, and an outward feather reads as a halo.
5. Decision: ornaments at the scene's edges in the open sky, not attached to the window's edge.
   Rationale: both act on the whole scene; a platter opening from a window-attached ornament on a
   texture path lands over the window and shows sky where the eye expects the window's glass (seen
   in both first placements and moved).
6. Decision: 32 px of air as the composition's floor over the derived gap. Rationale: the tuned
   material's padding is 20–24 px and the composition wanted room; the law is "at least".
7. Decision: real data rather than a painted sky. Rationale: the catalogue, NASA's maps and
   astronomy-engine make the environment true, which is what makes it content.
8. Decision: the Moon and the Sun at five times their angular size. Rationale: at half a degree
   the Moon is four pixels; every planetarium enlarges it; recorded on the canvas's own label.
9. Decision: no tint anywhere. Rationale: the environment carries the colour; nothing on the page
   needs finding first.
10. Decision: the sweep on materialise only. Rationale: motion rationed by frequency; arrival is
    once.
11. Decision: no panel, audit plus review. Rationale: I.

## Surprises & Discoveries

1. Observation: neither the clear base σ (0.05 to 30) nor its tint alpha (0 to 0.9) changed the
   window body's flatness: the body samples the pyramid's heavy level at window span
   (`sizeScatterGainMax` 8 → the chain's last level) and mixes it in by a share that rises with
   span. Gain 1 was the lever. Evidence: `tmp` captures `t-sigma30`, `t-alpha09`, `t-scatter`;
   `wgsl/optics.ts` "The scattering facet of the size law".
2. Observation: with the scatter down, the light material still drew the window at encoded 0.42
   over a 0.15 sky — the dead band — because the fitted tone response (and its black branch, 132
   codes over black) solves the body's alpha up to Apple's level. Standing both down for clear
   made the body the sky. Evidence: the first audit's light-scheme worst line, "Moon" at 4.13
   against ground (108, 106, 107); `x-night-light`.
3. Observation: the size law's occlusion facet (0.05) is invisible on the dark material's neutral
   (0.05 grey) and a grey plate on the light one (white). Evidence: `v2-light` before, `x-night-light`
   after.
4. Observation: a lens over a source with fine grain (the Milky Way layer's faint Gaia stars)
   draws contour-like ripples across the body; and a per-frame dither under the lens crawls. Fixed
   in the source (a 1.1 px Gaussian on the map; the page draws its own stars) and by a fixed
   dither pattern. Evidence: `c-module` before, `c2-module` after.
5. Observation: `directionOfObject` took degrees where every caller passed radians; the card
   named the Moon ENE while its row said ESE, and the drawn Moon stood in the wrong place. Found by
   writing the unit test the projection header had promised. Evidence: `test/planetarium.test.ts`.
6. Observation: `samplingPaddingFor` takes a `variant` on 0.24.0; the tracker entry that says a
   layout cannot derive its gap for clear is stale on that point (the missing signal on a runtime
   variant switch stands).
7. Observation: `half` is reserved in GLSL ES 3.0; React's strict effects mount a WebGL canvas
   twice and a lost context compiles nothing for the second mount.

## Deferred

- The user's eye on the page, and a line on whether this is the register Harvestar wants.
- A four-rater panel on the spatial rulebook, if the page is to join the two spatial pages' proof.
- The runtime reading clear's `adaptation: "constrained"` and drawing its dimming layer: this
  page is one implementation of both, in a tune and a painted layer, and the tracker entry stands.
- A tune that is a document: the six leaves as a "clear-lens" endpoint the runtime could ship as a
  named material rather than a page's `materialProfile`.
- Constellation names on hover; the ISS; a hemisphere-aware Moon glyph.

## Outcomes & Retrospective

**The page.** `apps/demo/src/gallery/planetarium/`: a WebGL2 sky (9,096 catalogue stars, NASA's
Milky Way and figure layers, astronomy-engine's Sun, Moon and planets, twilight and day, a ridge),
one window, one module and two morphing ornaments in the clear variant tuned by six named leaves,
the dimming layer painted adaptively under each host, the materialise sweep driven, press inside
the platters written by the page. Lint, typecheck, the demo's unit suite (64, seventeen of them the
sky model's) and the gallery e2e claim (both schemes) pass; the site builds.

**The readings.** The final audit, the fourth, after the review's fix wave (2026-09-28,
`docs/research/data/2026-09-28-planetarium-flagship/`):
zero diagnostics on both channels in every pass, zero ban findings on both lists, no host in the
ink dead band in any state, forced colours draw no glass, reduced transparency through the page's
switch moves the material; every text line on glass at or above its floor in every state read —
light 306 of 306 (worst 5.10) and 218 of 218 across the four phases (4.69), dark 306 of 306 (6.12)
and 218 of 218 (5.46), the CSS tier 306 of 306 (5.15) and 218 of 218 (4.68), the receded pose 241
of 241 (5.10), reduced transparency 55 of 55 (6.45); the third audit, before the wave, read the
same. The first audit had 227 readings below the floor and the second 35; each round's cause and
fix is in the record's part two. The captures (68 audit captures and 10 of the page's states) are
hashed in `captures.sha256` and archived as GitHub release `planetarium-flagship-2026-09-28`
(zip SHA-256 400298c3b30738209d134f0f1920f1c86b0cba1ff9feb9c9bc9066c28b9d56b1).

**What the initiative learned.** (1) At window span the clear variant is opaque by the regular
material's fitted laws — the scatter chain's heavy level, the size law's occlusion facet, the tone
response with its black branch — and not by its own base blur or tint alpha; a page that wants a
lens has to name those three, and the runtime's tuning API lets it (tracker). (2) The dimming
layer can be the clear variant's adaptation: measured per host, it takes a night sky at the floor
and shades a noon sky to a level white ink reads on, the same page, no scheme pin. (3) A lens over
fine grain ripples and over a per-frame dither crawls: an environment for a lens is smoothed where
it is noise and fixed where it is dither. (4) Two placements that the register's rule forbids —
a platter opening over a window on the texture path — came from attaching scene-wide ornaments to
the window; hanging them at the scene's edges resolved both. (5) The test the projection header
promised found the unit bug the eye had read as a compass octant.

**Purpose.** Met for what the session can judge: one page, the whole runtime surface, optical
rather than frosted, measured clean. The user's eye is not in this record.

## Revision Notes

- 2026-09-28: chartered from the user's ask in the main session; the page built, swept and
  audited three times the same day. The independent review (`doperpowers:reviewer-high`) returned
  twelve findings, ten must-fix (narrow-viewport layout; the closed morph face's one-time width;
  the Timeline's moving origin; the selection ring's stale coordinates; the Moon's limb direction
  by chord; DST in local noon; twilight classified on refracted altitude; the next twilight event
  at high latitude; a leaked measurement texture; no keyboard path for turning the sky) and two
  minor (radio-group arrows; Tab out of a platter). One fix wave closed all twelve with a probe
  or unit test each; the record's part two lists them. The session then took three seams the
  wave saw and left, and lowered the standard arrangement's height gate to 700 with the fit test
  protecting it (Decision Log 12). A fourth audit reads the page as it ships (Outcomes).
- Decision Log 12. Decision: the standard arrangement is tried from 1240 × 700, the compact one
  below, the clamped one under about 1024 × 700; a fit test decides, not the gate alone.
  Rationale: the reviewer's finding 1; the wave's observation that 1366 × 768 and 1440 × 780
  fit the standard arrangement in full; the record names 1024 × 700 as the minimum.
