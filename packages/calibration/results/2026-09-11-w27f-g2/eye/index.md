# W27f G2's eye sheet

Two sheets, one per colour scheme, for the user's eye on the material over ordinary page content.
**The eye is the parent's to take; this gate prepares the sheet and claims nothing from it.** W27f's
charter ends with "the user's eye on the demo's DOM stage", and claims §5.131 §8 hands G2 that
clause explicitly alongside the native stack bound.

> **Taken, 2026-09-12. The user looked at both sheets and ruled: "passes; residuals stand as
> recorded."** The sentence above is kept as it was written, because it is the true record of what
> this gate could and could not claim when it built the sheet — the ruling is the user's and arrived
> after. The three residuals the sheet exists to show are accepted as **gaps, not blockers**, and
> stay in the ledger as future work: the light photo overlay's rim overshoot, the photo base's
> colour, and the unhinted dark overlay's brightness. None is closed. Claims §5.135 §10 records the
> ruling; W27f's acceptance clause for the user's eye is met.

| file | size | what it carries |
| --- | --- | --- |
| `eye-sheet-light.png` | 4720 × 6108 | six comparison rows and the live demo stage, light |
| `eye-sheet-dark.png` | 4720 × 6082 | the same rows in the dark scheme |

## What to look for

Claims §5.131 §6 names three residuals that its metrics record but do not settle. Each has a row:

1. **The light overlay's rim is stronger than Apple's.** Row 1, light sheet, both stacks. Apple's
   inner plate carries a bright, tight rim; vitrea's is close on the checkerboard
   (rim local excess 0.109977 against native 0.111642) and **overshoots on the photo**
   (0.109090 against 0.084228). The sampled and page panels differ from each other far less than
   either differs from Apple.
2. **The photo base's colour.** Rows 1 and 2, the `photo` cells. The metrics improved — the light
   photo pane's whole-footprint ΔE fell 0.03475 → 0.01896 in G1 — while the colour of the body over
   a structured, saturated backdrop still reads differently from the fixture.
3. **The dark unhinted overlay is too bright.** Row 1, dark sheet, rightmost panel. Its overlay
   luminance is 0.049707 against native 0.020698 — more than twice — and it is obvious without
   measuring. This is the information limit, not a coefficient error: a DOM group with neither
   pixels nor a declared tone cannot tell a dark page from a light one (§5.129 §2, §5.131 §1).
   The same panel in row 2's `dark-solid__capsule-button__rest` is the collapse failing outright.

Then the thing the metrics cannot reach at all: **row 3, the live site**, drawing over its own
paragraph text rather than a calibration raster. Whether that looks like the material Apple ships is
the judgement this sheet exists to support.

## How to read a row

Left to right: Apple's fixture where one exists, then the same scene drawn three ways —
`sampled` (the registered texture path; **S1** on a stack), `unsampled-hint` (**Uh**, the page path
at its measured backdrop level, which is what W27f landed), and `unsampled-nohint` (**U0**, the page
with no hint at all). U0 is on the sheet as the limit, not as a candidate: it is outside the gate's
bound by declaration (`declaration.md` §2).

On the stack rows, **look at the small inner plate**. That overlay resolves `css-backdrop` in every
configuration, which is why the stacks are the only native evidence of the DOM-sourced path
(§5.129 X8). The large plate beneath it is the base, and the base is what changes between the three
web panels.

## Scale, and the one departure from native pixels

The calibration bed is 1x, so every fixture and capture here is 320 × 200 device pixels. They are
magnified **×2 by nearest neighbour**: each source pixel becomes one 2 × 2 block. That is exact and
reversible — it invents no value and moves no edge — and it is the only way a 320-px panel can be
looked at beside the demo's 1584-px stage. Every such panel says `1x ×2 NN`. The demo panel alone is
native device pixels at devicePixelRatio 2, and says so. The ruler is true for both, because ×2 of a
1x capture and native dpr 2 are the same number of device pixels per CSS pixel.

The 0.16.0 sheet took the opposite choice — 2x fixtures throughout, nothing magnified. Either is
honest as long as the sheet says which; this one is at 1x because 1x is the bed this gate measured,
and putting a 2x fixture beside a 1x reading would be the comparison the sheet is not making.

## The absent dark photo stack

`apple-macos-26.5-1x-dark-standard` carries no `photo__glass-over-glass`, at 1x or 2x — the dark
profiles' scene lists never asked for one. Its native panel is a labelled hole. Nothing is
substituted into it: not the light fixture, not the dark checkerboard stack. That cell is declared
unbounded (`declaration.md` §1) and no reading of it is adopted.

## The machine, the browser and the adapter

- **Chromium 151.0.7922.34**, `channel: "chromium"` (the full browser, headed) with
  `--enable-unsafe-webgpu --enable-features=Vulkan,WebGPU`. Never the headless shell, whose
  SwiftShader would pass a CPU rasteriser off as the GPU tier.
- **Adapter `apple` / `metal-3`, `isFallbackAdapter` measured `false`.** Measured is the operative
  word: the flag lives on `GPUAdapterInfo`, not on `GPUAdapter` (root spec Decision Log #36(b)), and
  the 0.16.0 sheet's harness read it off the adapter and defaulted it with `?? false`, so its
  recorded `false` was never measured and its guard could not fire. `capture-demo.mjs` reads the
  info object and keeps the value tri-state: only a measured `false` passes, and an absent flag
  refuses.
- The site's own readout was scraped at the moment of each shot and is printed under the panel:
  `dom / webgpu / css-backdrop / approximate / none / ok / none` in both schemes. The capture
  refuses if "What is drawing" is not `webgpu`. **Zero console warnings or errors** in either scheme.
- `devicePixelRatio` 2. macOS Reduce Transparency and Increase Contrast both **off** (verified `0`);
  Playwright cannot emulate either, so the sheet would silently be a different material if they were
  on.
- The colour scheme is driven through the site's own `<select>`, not the context option: the demo
  hard-codes its initial state to `light` and only consults `prefers-color-scheme` on `auto`. The
  applied value is read back from `documentElement.dataset.colorScheme` before the shot.

## The exact commands

```bash
# the captures the rows are made of already exist under the run's scratch root;
# see claims §5.135 for the runner and its invocation
cd <repo>
pnpm --filter demo exec vite --port 5233 --strictPort &     # not 5189: see the tracker
cd packages/calibration/results/2026-09-11-w27f-g2/eye
node capture-demo.mjs --base http://localhost:5233 --out ./panels
/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python compose.py --scratch /tmp/w27f-g2
```

`panels/` is **not committed** — it is the raw capture, regenerated by the command above — except
`panels/demo-meta.json`, which is, because it carries the adapter, the Chromium version, the site's
resolved readout and the console record.

## Files here

```
eye/
  index.md                this file
  eye-sheet-light.png     the light sheet
  eye-sheet-dark.png      the dark sheet
  capture-demo.mjs        the demo capture, with the adapter guard that actually fires
  compose.py              builds the sheets from the fixtures, the scratch captures and panels/
  panels/demo-meta.json   adapter, Chromium, the site's readout, the console record
  panels/<scheme>/        NOT COMMITTED — the raw device-pixel demo captures
```
