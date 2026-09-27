# Photo review: the record

A desktop culling and adjustment tool for a working photographer, built on vitrea 0.24.0 through
`@vitreajs/vitrea-react` under the materialist skill. The job is culling: look at a frame,
decide (reject, rate, pick), fix what needs a quick fix, move on. The design is weighed against
that loop, which repeats about thirty times in this shoot and several thousand times in a real
one.

The lines below were written before the first host was registered, and amended where a source
review's fix wave (2026-09-27) changed the page or found a line had drifted from it: the groups,
family, motion and contrast lines. Sections after the record say what was decided while building
(decisions 12 to 14 are that wave's), what the runtime resolved, what was seen and which phases
of the plane are flat.

## The record

```
plane: one canvas, fixed to the viewport above the filmstrip band, registered as the texture
  source "stage" and painted at its own box's device size, so screen and texture are the same
  pixels. It paints a neutral surround and the selected frame fit whole, with the frame's
  exposure, white balance, straighten and crop matte already applied (and in crop mode the
  crop frame and the thirds grid), so everything the glass bends is in the texture. Broad
  frequency: the firelit frame's tonal masses (hearth glow, window light, the dark shop). Fine
  frequency: tools, chains, brick, stock, sparks, grain, and in crop mode the painted grid.
  The frames are low-key; every surface was placed by measuring the ten photographs under
  candidate boxes (mean, deviation and edge energy): the corners are vignetted near-black on
  four photographs of ten, the middle of the trailing edge and the top and bottom centres
  carry structure on all but one or two. The glass sits only inside the photograph's
  rectangle, never over the flat surround.
inventory: three surfaces, read aloud: the tool palette, which is also the adjustment platter
  (one host for its whole life: a vertical capsule of three tools at the photograph's
  trailing edge, grown in place into the platter of the chosen tool's controls; base plane
  closed, overlay while open); the compare toggle, Before | After, top centre (base); the
  verdict bar, reject | rating | pick, bottom centre (base). The platter is the one transient.
  Opaque, on the tonal ground: the shoot column at the leading side (shoot, cull tally,
  keys, the reduce-transparency setting, credits), the frame column at the trailing side
  (histogram, frame data, adjustments, this frame's credit) and the filmstrip band beneath
  (thirty thumbnails with flags and ratings), one tonal step below the ground with a hairline.
groups: tools = the palette/platter morph; compare = the segmented toggle; verdict = the
  verdict bar. All three read the texture "stage" and also declare a hint measured from the
  pixels the page painted under the box the runtime DREW that group at (the union of its
  members' bounds in `root.renderInput()`: mean linear luminance, a tone from the mean and
  the share of light and dark pixels, complexity from the deviation), re-measured whenever
  the stage is repainted or that drawn box moves by a device pixel. A declared hint overrides
  the runtime's own tone reading on both tiers, so it describes the glass where it is, never
  where the layout means it to be. At 1440 x 900 the nearest pair (verdict to the open
  platter) is about 48 px apart horizontally and 120 px vertically; nothing pins a sampling
  padding.
family: thickness 8 across all surfaces. S 40: compare, capsule r20. M 52: palette and verdict
  bar, capsule r26; the palette is a 52 x 140 border box on both tiers, r26 being half its
  span. L 340 x 244 (span 244): the platter, fixed r26, the palette's own radius,
  because the platter is the palette grown and its tool column must stay concentric with the
  corner in both states. Anchor: the photograph's rectangle at r0 (a photograph has square
  corners); every surface is inset 16 from its edges, so nothing is concentric with the plane
  and that is the recorded web reading. Inner radii as housing minus inset: tool buttons r20
  (26 - 6), verdict buttons r20 (26 - 6), compare indicator from the runtime's resolver
  (about 20 - 3), platter fills r10 (26 - 16), option segments inside a fill track r8 (10 - 2).
tint: none. A hue 16 px from a frame biases the white-balance judgement this tool exists to
  make, so the control layer is achromatic; the only chroma on glass is the temperature and
  tint slider tracks, where the hue is the value being set.
scheme and pose: colorScheme auto, tokens following prefers-color-scheme. Light: a neutral
  light-grey ground (a print on a light mat). Dark: a neutral near-black-grey ground. Every
  neutral r = g = b in both. windowActivation auto; the receded pose is looked at, not pinned.
motion: the palette grows into the platter and back as one matched-geometry morph (the tool
  column holds still while the panel is revealed); when the window moves the palette with the
  platter open, the platter closes onto the palette where it now is and re-opens there; the
  compare indicator slides on the runtime's springs; press is the runtime's glow and
  compression on the closed palette, the compare toggle and the verdict bar, and on the open
  platter, whose host the runtime makes non-interactive, the page drives the same two channels
  on the host from the root's motion profile when a plain control inside is pressed; the stage
  changes frames with no transition at all, because a photographer needs the next frame now;
  nothing moves at idle. Reduced motion is the runtime's profile, which the platter's press
  reads too: no compression, the glow kept.
tier expectation: webgpu requested (localhost is a secure context); css on ?renderer=css and
  wherever the engine has no adapter; the CSS tier is the same page without refraction and
  without the body's hue.
accessibility: the runtime follows the system for motion and contrast; reduce transparency is
  an app setting in the shoot column, seeded from the media query where the engine answers
  it and from a stored preference otherwise, always passed to the root as a boolean. Under
  forced colours the glass goes and the controls remain real buttons with visible state.
contrast: labels and icons take the pole of the runtime's published primary ink at full
  strength on child elements (decision 7); measured on rendered pixels over every frame of the
  shoot in both schemes (results below).
```

## Thirty frames from ten photographs

The ten Unsplash photographs in `images/` are shown as ten bursts of three exposures. The second
and third frame of each burst are the same file re-framed by a few per cent (the camera moving
between frames) and bracketed by a third of a stop, painted by the page. Filenames, times and
exposure data are invented for the demo and say nothing about the photographers' own cameras.
The page says so beside the credits.

## Decisions made while building

1. **The verdict bar is on the inventory although the brief did not name it.** The job is culling,
   and reject, rate and pick is the act repeated on every frame. It is an action, it floats, and it
   is the bar's only content. Keys carry the same verdicts (P, X, U, 0 to 5).
2. **The palette sits at the middle of the photograph's trailing edge.** It was placed by measuring
   the ten photographs under candidate boxes, not by convention: the corners are vignetted
   near-black on four photographs, and the trailing middle had the fewest flat phases. Trailing,
   too, so the exposure slider opens beside the histogram in the frame column.
3. **The platter grows in place.** `GlassMorph` places its open end relative to the closed
   footprint (`below-end`), and a gap of minus the palette's own height (-140) puts the platter's
   top-right corner on the palette's. While the morph travels the host is a right-aligned,
   top-aligned flex box, so the tool column stays where the palette was while the panel is
   revealed leftward; at rest its content is centred (decision 13). The runtime's open-end default
   thickness is 14; both ends are pinned to 8 to keep one thickness across the family.
4. **One platter size for all three tools (340 x 244).** `GlassMorph` measures the open end when it
   opens and does not re-measure while open, so a tool switch that changed the content's size
   would clip or leave a hole. The exposure panel carries the empty space as a result.
5. **A crop is a matte over the whole frame rather than a re-fit.** The frame's rectangle is the
   same for all thirty frames (all 3:2), so the controls never move while culling at speed. There
   is also a runtime reason: an open morph does not follow its footprint (it realigns only closed
   and settled), so a crop that re-fit the frame would have stranded the open platter off the
   photograph. The matte washes the cropped-away frame 66 % toward the ground (50 % in crop mode,
   with the frame, corners and thirds grid painted into the texture). It was 80 % first. Looked at
   on frame 8, that left the palette over an almost flat, almost white field, so it came down.
   A portrait frame would still move every control, and that case is not in this shoot.
6. **Hints are measured, not declared by hand, under the drawn box.** The page reads the canvas
   under the box the runtime drew each group at, from the frame's own render input: mean linear
   luminance (the hint's `luminance`), a tone, and a complexity from the deviation. It re-reads
   whenever the stage is repainted or a drawn box moves by a device pixel, which on the morph is
   every frame of a flight and then never. The first version read the box the layout intended,
   and an open platter left behind by a window change made that a statement about somewhere the
   glass was not (decision 12).
7. **Label ink: the runtime's pole at full strength, over opposite-pole wells.** Measured first with
   the published primary (0.85 black, 0.8 white alpha): the dark scheme's "Before" label read
   3.25:1 on frame 7. The selected compare segment, filled with a tint of the ink, read 3.9:1 in
   light, and chips filled the same way read 3.3:1 on the dark platter. Three changes followed.
   Labels take the runtime's pole at alpha 1. Every fill under text is the ink's opposite pole (a
   well), never a tint of the ink, which is the skill's "authored colour on a child" moving the
   surface out of the band where neither ink carries text. Each slider sits in a concentric well,
   the way Control Center groups controls, because bare labels on the dark platter read 4.2:1
   over frame 12's plaster wall. The panels' headers were removed, since the selected tool already
   names the panel and they were the last bare text on glass.
8. **The slider knob is a fill.** Apple lifts a knob into glass while it is dragged; vitrea refuses
   nested glass in both directions, so on the web it stays a fill.
9. **One loop.** The stage paints, and the hints are measured, from the root's ticker when
   something changed; the platter's press joins the root's own frame loop for the length of a
   press (decision 14). Nothing runs a second `requestAnimationFrame`. The histogram is
   achromatic like the rest of the chrome.
10. **Focus follows the tool across the morph.** The closed and open ends are different DOM, so the
    button the reader pressed unmounts. The matching button in the other end takes focus as it
    mounts. A swap the palette did not make, a key or decision 12's close and re-open, carries
    focus the same way when focus was on the palette.
11. **The stage has no transition between frames**, and nothing moves at idle.
12. **An open platter follows the window by closing and re-opening.** An open `GlassMorph` keeps
    the box it opened at; it re-follows its footprint only closed and settled. The source review
    found that from 1440 x 900 to 1280 x 800 the open platter was left off the photograph, over
    the frame column. Now a window change that moves the palette closes the platter, which
    carries it back onto the palette where it now is, and re-opens the same tool once the morph
    is at rest and the window has held still for 150 ms, so a live window drag does not open and
    close it repeatedly. Focus on the palette follows the tool through both swaps, and a reader's
    own tool change in between cancels the re-open. Verified on both tiers and schemes: after
    that resize the platter is drawn at 720, 271, 340 x 244, the box the new layout places, and
    its hint was read under that box.
13. **The palette's host is a border box.** The CSS tier writes a 1 px transparent border on
    every host as layout, and `GlassMorph` sizes its host from its content, so as a content box
    the palette was 54 x 142 on the CSS tier with a fixed r26, not the 52 capsule the family
    declares. The WebGPU tier registered the same 54 x 142 while the element measured 52 x 140:
    a GPU-requested root draws its first frames on the CSS tier (traced: eleven frames with the
    1 px border, then WebGPU and no border), the runtime measured the host then, and it kept that
    rect after the border went because its geometry sync observes each host's content box
    (`packages/platform-web/src/geometry-sync.ts` lines 260 and 317 call `observe()` with no
    `{ box: "border-box" }`, while the comment at 164 says border-box). That is a runtime
    finding for the runtime's own tracker. As a border box the host is 52 x 140 closed and
    340 x 244 open on both tiers, and since the border's removal now changes the content box, the
    runtime re-measures. The content, 2 px larger than the padding box where the border exists,
    is centred at rest, so the tools sit 6 px inside the outer edge on both tiers and stay
    concentric at r20; in flight it is right- and top-aligned as before, so on the CSS tier alone
    the column steps 1 px as a flight starts and ends.
14. **Press on the open platter is driven by the page, through the channels.** `GlassMorph` makes
    its host non-interactive while open, because what a reader presses then is the content, and
    the content here is plain buttons, fills and range inputs, never glass. So the page does for
    the platter what the runtime's own interaction does for a control (`press.ts`): a pointer
    press or a Space/Enter on any enabled button in the platter writes `--vitrea-press`,
    `--vitrea-glow` and the press point on the host (`GLASS_CHANNEL_PROPERTIES`), stepped on the
    springs and state targets of the root's motion profile (`useGlassMotionProfile`), and hands
    the channels back at rest or the moment the platter morphs. The morph writes its own glow
    every frame (`packages/react/src/morph.tsx` line 501), so the page joins the root's frame
    loop when the press begins, which puts its write after the morph's. No transform and no
    colour. Measured on the WebGPU tier: pressed, the runtime's render input reads press 1.00 to
    1.02 and glow 0.97 to 0.99 at the chip's contact point, and the drawn platter's edges move in
    about 3 px left and right and 1 to 2 px top and bottom, the profile's 1.5 %; released, press
    bounces to -0.04 and settles as the glow decays. Under Reduce Motion the profile removes
    compression (press stays 0.0000) and keeps the glow (0.97). What the CSS tier draws is the
    glow from the press point and no compression, because its compression is the host's owned
    transform, which only the runtime can write; the app has no handle to the morph's host. A
    range input's drag does not press the platter: the knob is what moves.

## What the runtime resolved

Read from `window.__vitrea` (`capabilities(groupId)`, `material`, `accessibility`,
`windowActivation`, and both diagnostics channels) in Chromium (`channel: "chromium"`,
`--enable-unsafe-webgpu`) on localhost at 1440 x 900.

| state | tools, compare, verdict |
|---|---|
| default (GPU requested) | `webgpu` / `gpu-texture` / refraction `true` / analysis `exact` / health `ok`, all three |
| `?renderer=css` | `css` / `css-backdrop` / refraction `none` / analysis `hint` / `ok`; `cssBody` `collapsed` in light, `two-layer` in dark |
| material | `apple-macos-27.0-1x-light-standard-glass0.5` (`be13dae45098fc89`), the dark key under dark, `tuned: false` |
| reduce transparency (app setting) | frost `increased`, refraction `reduced`, occlusion `increased`; groups still `exact` |
| forced colours (emulated) | glass `none`, occlusion `opaque`, colour source `system` |
| window unfocused | `windowActivation: inactive` (Playwright emulates focus, so `document.hasFocus` was overridden and `blur` dispatched to see it) |
| geometry (render input) | tools 52 x 140 r26 closed, 340 x 244 r26 open; compare 166 x 40 r20; verdict 278 x 52 capsule r26; the same on both tiers |

**Diagnostics: zero on both channels** (`window.__vitrea.diagnostics.reported` and
`window.__vitrea.scene.diagnostics.reported`). Re-read after the fix wave on both tiers and in
both schemes at rest, with the exposure platter open, while pressing a control in it, after
resizing the viewport from 1440 x 900 to 1280 x 800 with the platter open, under Reduce Motion,
and through the thirty-frame contrast sweeps below, reduced transparency included. The maker's
earlier reading covered crop mode, forced colours, unfocused and 1920 x 1080 as well, also zero,
and found three `quaternary-ink-on-thin-material` warnings on the way from the verdict bar's
separators, which now take the tertiary token.

## Contrast, on rendered pixels

Method: at each of the thirty frames, screenshot once with labels and once with every glass label
and icon set transparent. Composite the label's computed ink over each background pixel under the
label's box (the text's own line box, or the icon's), and take that box's 10th-percentile and
median ratio. The table gives the worst label for each control class across the thirty frames
(p10 / median, and the frame): at rest, then with the exposure and the white-balance platters
open, whose tool column replaces the palette's. Text needs 4.5:1; icons and controls 3:1.
Re-measured after the fix wave (2026-09-27), Chromium at 1440 x 900, both schemes, both tiers.

| state | icons (tools, verdict) | compare text | platter text | chips and options |
|---|---|---|---|---|
| light, GPU, at rest | 5.61 / 5.62 (25) | 7.91 / 7.95 (26) | | |
| light, GPU, each platter open | 6.49 / 6.52 (10) | 7.91 / 7.95 (26) | 9.79 / 9.80 (17) | 9.80 / 9.80 (17) |
| dark, GPU, at rest | 4.08 / 4.12 (1) | 6.21 / 6.70 (7) | | |
| dark, GPU, each platter open | 4.08 / 4.12 (1) | 6.21 / 6.70 (7) | 6.18 / 6.64 (12) | 5.71 / 5.80 (6) |
| light, CSS | 5.61 / 5.61 (17) | 8.03 / 8.03 (26) | 9.14 / 9.14 (17) | 9.14 / 9.14 (17) |
| dark, CSS | 4.06 / 4.12 (1) | 6.27 / 6.63 (7) | 6.58 / 6.79 (12) | 6.48 / 6.56 (6) |
| reduce transparency, GPU, light / dark | 18.26 / 9.62 | 18.93 / 12.23 | 18.93 / 11.86 | 18.93 / 11.36 |

At the frame the page opens on (14) and at the flattest phase in the flat-phase table (frame 26,
the compare toggle at 0.004), the lowest label in any of the three states on the GPU tier reads:
light, icons 8.06 and text 10.40 on frame 14, icons 7.64 and text 7.91 on frame 26; dark, icons
5.16 and text 8.34 on frame 14, icons 8.64 and text 9.39 on frame 26. The palette's own flattest
frame, 17, reads icons 5.69 in light and 7.69 in dark. The dark minimum is frame 1's verdict
stars at 4.08, over a mid-tone region (the verdict box's mean is 0.47 of full scale), not a flat
phase.

The opaque columns use the page's own neutrals: `--ink-2` on the ground is 6.3:1 in light and 6.8:1
in dark by calculation; on the band it is 5.6:1 and 7.3:1.

## What was seen

- On the GPU tier the body carries the photograph's colour: over frame 14 the palette runs from
  the glove's orange at its top to the denim's blue at its foot, and the verdict bar takes the
  anvil's grey. The receded pose greys all three surfaces (the runtime draws it with no exterior
  shadow; that was not measured here), and the selected compare segment keeps its pole.
- The frames are low-key, so some phases are near-flat under a surface; the next section lists
  every one.
- Pressing a chip on the open light platter lights the platter from the contact point and draws
  its field in by about 2 to 3 px a side (1.5 %), and the pressed chip's own label reads faint
  under the glow for the length of the press, because the highlight plane is drawn above the
  host's DOM. That plane order is the runtime's, for its own controls as well; the pressed
  state's contrast was not measured and is recorded here as a difference the eye sees.
- The CSS tier is the same page without refraction and reads close to the GPU tier over these
  frames. In light it resolves the body `collapsed` (one layer).
- Reduced transparency turns every surface into a near-opaque frosted plate with the same
  hierarchy; that is the state, not a failure.

## Flat phases, measured

Method: for each of the thirty frames as the shoot opens (each frame's own crop and develop), the
page reads the stage canvas under the box the runtime drew each surface at and takes the standard
deviation of the pixels' encoded luminance, 0 to 1 of full scale (`regionReading` in
`develop.ts`, sampling every second pixel). A phase is **flat** when that deviation is under
**0.03**: about eight 8-bit codes, where a photograph's texture has gone and only a vignette or a
matte's wash is left. Reproduce it from the console: `__glassDemo.select(i)` steps to frame
`i + 1`, and `__glassDemo.backdrop()` returns each group's drawn box, deviation and mean once that
frame is painted. Boxes at 1440 x 900: palette 1168, 320, 52 x 140; compare 637, 62, 166 x 40;
verdict 581, 666, 278 x 52; platter 880, 320, 340 x 244 (read with the exposure platter open).
The two schemes read the same except where a crop matte, washed toward the scheme's ground, falls
under the box; that cell gives light / dark.

| frame | palette (closed) | compare | verdict | platter (open) |
|---|---|---|---|---|
| 1 | 0.046 | 0.108 | 0.090 | 0.178 |
| 2 | 0.041 | 0.110 | 0.085 | 0.152 |
| 3 | 0.053 | 0.112 | 0.100 | 0.206 |
| 4 | 0.065 | **0.017 flat** | 0.073 | 0.238 |
| 5 | 0.059 | 0.115 | 0.049 | 0.227 |
| 6 | 0.070 | 0.134 | 0.047 | 0.254 |
| 7 | 0.043 | 0.217 | 0.128 | 0.193 |
| 8 | **0.017 flat** | 0.094 | 0.107 | 0.182 / 0.059 |
| 9 | 0.045 | 0.122 | 0.135 | 0.209 |
| 10 | 0.123 | 0.041 | 0.067 | 0.222 |
| 11 | 0.155 | 0.050 | 0.080 | 0.229 |
| 12 | 0.157 | 0.055 | 0.080 | 0.239 |
| 13 | 0.137 | 0.199 | 0.151 | 0.191 |
| 14 | 0.147 | 0.141 | 0.127 | 0.161 |
| 15 | 0.164 | 0.094 | 0.127 | 0.195 |
| 16 | 0.118 | 0.071 | 0.126 | 0.104 |
| 17 | **0.006 flat** | 0.057 | 0.108 | 0.095 |
| 18 | 0.120 | 0.065 | 0.123 | 0.112 |
| 19 | 0.139 | 0.235 | 0.065 | 0.157 |
| 20 | 0.082 | 0.209 | 0.050 | 0.151 |
| 21 | 0.155 | 0.254 | **0.027 flat** | 0.178 |
| 22 | 0.130 | 0.123 | 0.048 | 0.167 |
| 23 | 0.141 | 0.102 | 0.039 | 0.157 |
| 24 | 0.155 | 0.136 | 0.042 | 0.187 |
| 25 | **0.018 flat** | 0.226 | 0.107 | 0.197 |
| 26 | 0.137 | **0.004 flat** | 0.144 | 0.177 |
| 27 | 0.041 | **0.006 flat** | 0.208 | 0.220 |
| 28 | 0.091 | 0.229 | 0.123 | 0.139 |
| 29 | 0.095 | 0.165 | 0.108 | 0.129 |
| 30 | 0.108 | 0.170 | 0.119 | 0.158 |

At rest, 7 of 90 surface-frame phases are flat: the palette on frames 8 (the 4:5 matte over a
quiet wall), 17 and 25 (vignetted near-black); the compare toggle on frames 4 (the 16:9 matte over
a washed window), 26 and 27 (near-black); the verdict bar on frame 21. The open platter is flat on
none of its 30 (lowest 0.059, frame 8 in dark). Medians: palette 0.10, compare 0.11, verdict
0.10, platter 0.18.

Ruling (session, 2026-09-27): bounded by design intent, recorded rather than fixed. The plane is
the photographer's frame, and the page does not alter a photograph to give the glass something to
bend. Moving the controls per frame to find structure would cost the cull its fixed positions,
which matter more to a photographer working at speed than the faint edge. Over a locally flat
frame the material reads as its edge and shadow, and the macOS 27 material still draws a present
plate over black. That is the material's own behaviour over flat content, which Apple's glass
shows over a flat region too, not a failure the page can fix without touching the photograph.
The skill's ban on a flat field is about a plane designed flat; this plane is designed as the
photograph, and its flat phases are the photograph's.

## QA lens (materialist SKILL.md section 8)

1. `[layer]` Pass. The palette/platter, the compare toggle and the verdict bar are two actions and
   one transient platter; the tallies, histogram, metadata, credits and filmstrip are opaque.
2. `[layer]` Pass. Everything on glass is a fill, a range input or a plain button; the morph's inner
   tool buttons are not hosts.
3. `[layer]` Pass. Three surfaces; each carries a job no other does.
4. `[material]` Pass. Regular everywhere; no clear variant.
5. `[material]` Pass. No tint at all, and no solid fill or hand-rolled blur in its place.
6. `[material]` Recorded, ruled bounded by design intent. Every surface is over the photograph at
   every phase and never over the flat surround, but 7 of 90 resting surface-frame phases are flat
   under the 0.03 threshold, and 0 of the open platter's 30 (the measured table and the ruling
   above).
7. `[material]` Pass. No depicted material; the crop matte and grid are functional and painted.
8. `[geometry]` Pass. Capsules, one fixed radius and concentric fills (listed in the record); the
   anchor is the photograph at r0, named.
9. `[geometry]` Pass. The three single-row or single-column housings are capsules: the palette is a
   52 x 140 box at r26 on both tiers (decision 13; it measured 54 x 142 before), the compare toggle
   166 x 40 at r20, the verdict bar the runtime's `capsule` at 52; the platter is a 26 px rounded
   rectangle; inner controls are concentric, the tools 6 px inside the palette's edge at r20.
10. `[geometry]` Pass. Spans 40, 52 and 244 as the runtime registers them, thickness 8 everywhere,
    including the morph's open end.
11. `[grouping]` Pass. One group per surface. The verdict bar is all icon buttons; no text and icon
    buttons are mixed in one group. At 1440 the nearest pair is 102 px apart vertically, and no
    proxy-overlap diagnostic appeared, including under reduced transparency with the platter open.
12. `[legibility]` Pass, measured above after the fix wave, both schemes, both tiers, all thirty
    frames: lowest text 5.71 (dark GPU, a chip), lowest icon 4.06 (dark CSS, the verdict stars).
13. `[legibility]` Recorded deviation. The photograph is the plane, and the brief puts the controls
    over it, so content does sit under glass at rest. Nothing scrolls under glass, so no scroll edge
    exists. The cost is real for a photographer judging a frame, and closing the platter (Esc) is
    the only way to clear it. A hide-overlays state was considered and not built, because
    `GlassMorph` takes no `present`, so the palette could not dematerialise with the others.
14. `[legibility]` Pass for reduced transparency (the app's switch), forced colours (emulated) and
    the receded pose. Reduced motion was opened for the platter's press: the profile removes the
    compression and keeps the glow. Increased contrast is left to the runtime and was not opened
    separately.
15. `[layout]` Pass. The ground reaches every window edge; every floating position derives from
    the photograph's rectangle, which derives from the window, the open platter included: it
    closes and re-opens at the new geometry when the window moves it (decision 12). The stage is
    fixed and does not scroll.
16. `[layout]` Pass. No surface carries a background, border or scrim of its own.
17. `[motion]` Pass. The platter is one host growing from the palette; the compare indicator slides;
    press is glow and compression at the contact point, the runtime's on the three surfaces' own
    controls and the page's, through the same channels, on the open platter's plain controls
    (decision 14; the CSS tier draws that press as glow alone); nothing moves at idle; frames
    change without a transition.
18. `[colour]` Pass. The chrome is achromatic in both schemes; the only chroma on glass is the white
    balance tracks, where the hue is the value.
19. `[honesty]` Pass. Hints are read off the painted pixels under the box the runtime drew each
    group at, so they follow the platter through a morph and a window change; the resolved state
    was read back; diagnostics are zero at rest, with the platter open and after a resize with it
    open.
20. `[eye]` The nearest Apple surface is the adjust and crop controls of Photos for macOS 27. No
    native capture was available, so no comparison was made.
