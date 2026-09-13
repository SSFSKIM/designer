# W27e G3 — landing declaration, before source or browser movement

Committed before any source file moves and before any browser run. Claims section reserved:
**§5.142** (§5.141 belongs to W27c). Gate: W27 coverage wave, child W27e **G3 (land)**;
contracts **X1**, **X2**, **X4** and **X8**; Decision Logs **9**, **15** and **16**. Consumes
claims §5.137, §5.138 and §5.140. No Apple capture is taken, no material is fitted, and no bound
on the material is adopted here.

## 1. The complete label inventory

“Label” means every visible glyph rendered inside a vitrea glass host, including a decorative glyph
whose accessible name lives elsewhere. The inventory covers all three built demo entry points. A
changing label is one family below; every named state is exercised. The reference stage at `/`
renders an unlabelled `scene-surface` and therefore contributes no row.

| route / state | glass labels | floor |
| --- | --- | ---: |
| `/`, material | `112px` (or `112px, tinted`), `68px`, `40px` | **3.0**, the existing large-label pixel floor |
| `/`, ordinary page content | `112px`, `68px`, `40px` | **3.0**, the existing large-label pixel floor |
| `/`, tone sweep | `112px`, `68px`, `40px`, read through every declared ground stop | **3.0**, the existing large-label pixel floor |
| `/`, accessibility | `Regular material` | **3.0**, the existing large-label pixel floor |
| `/`, behaviour toolbar | `Share`, the `☆` / `★` favourite glyph, disabled `Publish` | **4.5**, WCAG body-text pixel floor |
| `/`, behaviour segmented control | `Day`, `Week`, `Month`, selected and unselected | **4.5**, WCAG body-text pixel floor |
| `/`, behaviour morph closed | `Actions` and its disclosure glyph | **4.5**, WCAG body-text pixel floor |
| `/`, behaviour morph open | `Duplicate`, `Rename…`, `Export as PNG`, `Delete` | **4.5**, WCAG body-text pixel floor |
| `/laws/`, tone | `112px`, `40px` | **3.0**, the large-label pixel floor |
| `/laws/`, tint | `over dark`, `over light` | **3.0**, the large-label pixel floor |
| `/laws/`, body | the live short-span label (`112px` at landing) | **3.0**, the large-label pixel floor |
| `/laws/`, lens | `lens` | **3.0**, the large-label pixel floor |
| `/laws/`, nested | `base`, `pane` | **3.0**, the large-label pixel floor |
| `/playground/`, DOM plate | `Regular material`; `dom backdrop · author hint` | **3.0** on the large heading; **4.5** on the body label |
| `/playground/`, texture plates | `Larger surface`; `deeper material, stronger lensing`; `regular` and its `clear` state | **3.0** on the large heading; **4.5** on the body labels |
| `/playground/`, segmented control | `Day`, `Week`, `Month`, selected and unselected | **4.5**, WCAG body-text pixel floor |
| `/playground/`, toolbar | `Share`, the `☆` / `★` favourite glyph, disabled `Disabled` | **4.5**, WCAG body-text pixel floor |
| `/playground/`, morph closed | `Actions` and its disclosure glyph | **4.5**, WCAG body-text pixel floor |
| `/playground/`, morph open | `Duplicate`, `Rename…`, `Export as PNG`, `Delete` | **4.5**, WCAG body-text pixel floor |
| `/playground/`, each light/dark ink plate | the names `primary`, `secondary`, `tertiary`, `quaternary` (all painted in primary ink) | **4.5**, WCAG body-text pixel floor |
| `/playground/`, each light/dark ink plate | primary `Aa` specimen | **4.5**, the body-text pixel floor used to guard primary ink |
| `/playground/`, each light/dark ink plate | secondary `Aa` specimen | **4.5**, Decision Log 9's secondary token promise, subject to §3's attribution |
| `/playground/`, each light/dark ink plate | tertiary and quaternary `Aa` specimens | **read, not gated**: these levels are documented below the body-text floor |
| `/playground/`, each light/dark ink row | bookmark `☆`; `Publish` | **4.5**, WCAG body-text pixel floor |

The run crosses every row with both colour schemes and both requested tiers (`webgpu` and `css`).
The requested WebGPU cells gate only when the resolved group state says `webgpu`; a software or CSS
fallback is not relabelled as GPU evidence. Every CSS-only fidelity difference is recorded under X1
rather than promoted into a WebGPU material claim.

## 2. Harness method

The one table-driven demo spec uses the method already shared by
`apps/demo/e2e/ink-band-contrast.spec.ts` and G2's `sheet.mjs`:

1. Recover each painter's computed ink **including alpha** by painting it through a 1 × 1 canvas
   once over opaque black and once over opaque white, then solve the two-pole source-over equation.
2. Read the surface from the glass host's own rendered screenshot. For ordinary controls and broad
   plates this is the host's median-luminance pixel. For a specimen, §3 separately tests the plate
   median and the pixel directly beneath the glyphs; whichever surface corresponds to the token's
   solve is the one the permanent floor uses.
3. Composite the recovered ink over that surface in encoded sRGB, convert both composited ink and
   surface to WCAG relative luminance, and only then take the contrast ratio.

No computed CSS colour string is treated as a contrast result, and translucent ink is never scored
as opaque. Dynamic backdrops are sampled at the existing four phases; the tone axis is walked across
its declared stops after the material transition. Every raw reading is written as JSON; §5.142
carries the readable table.

## 3. Secondary shortfall attribution, declared before the read

For the light ink plate's secondary specimen, record side by side:

- the token's two solve inputs: the selected ink pole and the exact surface colour(s) handed to
  `inkAlphaHoldingContrast`, plus the solved alpha and resulting ratio;
- the plate's current median rendered pixel;
- the rendered pixel under each sampled glyph interior after removing the glyph's own composite;
- the page ground byte and declared hint beneath the plate.

Attribute the 4.463 versus 4.5 difference to exactly one candidate with a number: **plate median**,
**the tint/composite used by the solve**, or **the declared backdrop differing from what is behind
the plate**. If the under-glyph surface accounts for the difference, move the harness to it and
restore the permanent pixel floor to 4.5. If the runtime's solved composite differs from the actual
under-glyph surface, keep a named pixel floor and record the solve input that must move in follow-up.
The tracker history is appended to, never replaced.

## 4. User-eye sheets

Produce one light-scheme and one dark-scheme sheet. Each sheet places the landing demo controls and
the `/playground/` ink plate beside the same views at `de9a9bcd`, the pre-G2 state. The captures use
the full Chromium binary on the hardware adapter, at one viewport and DPR, after the same settle.
The sheet records what to inspect and the implementer's own visual reading; it is not a substitute
for the user's verdict.

## 5. Stops

- **S1 — accessibility state.** Before every browser invocation,
  `defaults read com.apple.universalaccess reduceTransparency` and `increaseContrast` must both
  read **0**. If either reads 1, wait and poll; do not launch. Record both values beside that run.
- **S2 — inventory.** A declared selector finding zero or an unexpected count, a painter not
  reachable in one of its named states, or a newly discovered glass label absent above stops the
  landing until the declaration gap is recorded and the run is complete.
- **S3 — tier identity.** A WebGPU reading without `activeRenderer: webgpu`, a fallback adapter, or
  an unrecorded adapter is not evidence. Stop rather than call it the reference tier.
- **S4 — contrast.** Any body label below its named **4.5 pixel floor**, any large label below its
  named **3.0 pixel floor**, primary below 4.5, or secondary below the correctly attributed floor
  stops the landing. Tertiary and quaternary are measurements, not 4.5 gates; an inverted level
  order still stops as a ladder defect.
- **S5 — evidence integrity.** No existing evidence number, profile document, fixture, golden,
  `scenes.json` entry or canonical `results/matrix.json` row moves. No golden regeneration.
- **S6 — comparison identity.** A before/after eye pair with different viewport, DPR, scheme,
  accessibility values, route state or resolved tier stops the sheet; it is two experiments, not a
  comparison.
- **S7 — verification.** Workspace build/lint/unit, demo e2e, React e2e, and any platform pixel/GPU
  suite touched by the helper must be run at head. React Firefox failures in the named
  press/morph-materialize/presence flake class are recorded as such rather than rerun to green.

## 6. What this gate does not claim

No Apple pixel is captured or compared. The label evidence remains the coefficient/configuration
claim of §5.137–§5.140, not a native-pixel fidelity measurement. The large-label and body-label
floors above are harness pixel floors, not promises made by every token; Decision Log 9's narrower
promise is only the secondary's. Tertiary and quaternary carry no accessibility floor. The user's
eye remains a separate acceptance input after these records land.
