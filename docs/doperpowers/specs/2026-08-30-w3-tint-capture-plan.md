# W3 — the tinted-capture extension (2026-08-30)

> **Parent:** [the post-v1 wave](./2026-08-28-post-v1-wave.md) §W3. **Binds to:**
> X1 (the matrix is the bed), X2 (the profile-key contract).
> **Status: a plan, not a change.** Nothing in `apps/reference-apple/` or
> `packages/calibration/` has been touched. W3's phase 1 — the API, both tiers,
> the tests, the demo — is landed and carries **no fidelity number**; this
> document is what the measurement phase executes when the dispatching session
> schedules it, together with the harness rebuild and the TCC re-grant that a
> rebuild invalidates.

## What is actually unmeasured

Phase 1 ships one new optical mechanism, and it has exactly four free constants
(`MaterialProfile.tintTone{Floor,CeilMix,Low,High}` in
`packages/renderer-webgpu/src/material.ts`, mirrored as `TINT_TONE` in
`packages/platform-web/src/optics.ts`). They describe the curve that turns an
author's seed colour into Apple's "range of tones **mapped to content brightness
underneath** the tinted element" (S219):

```
tone(seed, backdropLuminance) =
  mix( seed × floor,                        // the shade, over dark content
       mix(seed, white, ceilMix),           // the wash, over bright content
       smoothstep(low, high, backdropLuminance) )
```

Everything else about the tint is either already-measured machinery it rides on
(the tint alpha, the tier conversion, the accessibility folds) or structure with
no free parameter (the seed displaces the neutral tint by the author's strength).
So the measurement question is small and sharp: **does Apple's tinted material
trace this curve, and with what constants?** Four parameters is what the cell
count below is sized for, and nothing more.

Two secondary questions the same captures answer for free, both of which are
*assumptions phase 1 made* rather than parameters it fitted:

- **Hue independence.** Phase 1 applies one curve to every seed. If Apple's tone
  range is hue-dependent — a blue tint darkening differently from an orange one —
  a single curve is the wrong model, and no amount of fitting fixes it.
- **Size and scheme independence.** Phase 1 makes the tone a function of backdrop
  luminance alone. Apple's material is size-parameterised on other axes (§3.2),
  and scheme-keyed on the neutral tint, so both are worth a cell rather than an
  assumption.

## The grammar: a scene axis, never a key axis

X2 is binding and settles this: *"new axes (tint scenes for W3) extend the scene
set, never the key grammar."* So no profile key changes. The six declared keys
capture tinted scenes exactly as they capture any other scene, and the
refuse-mislabeled-keys guard is untouched.

The scene id grammar stays three `__`-separated segments —
`{background}__{component}__{state}` — because two consumers parse it
(`packages/calibration/` and the scene page) and the split, the profile subsets
and the manifest all key on it. A tint therefore folds into the **third
segment**, as a suffix on the state:

```
photo__capsule-button__rest-tint-orange
dark-solid__capsule-button__rest-tint-blue
photo__capsule-button__rest-tint-orange-half
```

The id remains what it already is — the join key over declared axes — and the
tint is declared as its own registry beside `backgrounds` and `components`,
rather than being smuggled into either:

```jsonc
"tints": {
  "orange":      { "srgb": [255, 149, 0],  "$comment": "systemOrange. Warm, far from the material's neutral white, and the hue Apple's own tinting examples use." },
  "blue":        { "srgb": [10, 132, 255], "$comment": "systemBlue. The second hue exists to test that ONE tone curve serves every seed; a per-hue difference here refutes the model rather than retuning it." },
  "orange-half": { "srgb": [255, 149, 0], "alpha": 0.5, "$comment": "The strength axis. vitrea reads a colour's alpha as how far the material's tint moves toward the tone, and SwiftUI's Color carries opacity the same way — so this cell checks that the two agree about what half-strength means." }
}
```

and a scene entry gains one optional field:

```jsonc
{ "id": "photo__capsule-button__rest-tint-orange",
  "background": "photo", "component": "capsule-button", "state": "rest", "tint": "orange" }
```

**Why not a fourth id segment**, which would be the naïve shape: every existing
consumer splits on `__` and expects three parts, the split file lists bare ids,
and the six profile subsets list bare ids. A fourth segment is a migration across
four files to express something the third segment already has room for. **Why not
a new `states` entry** (`"tinted-orange"`): a tinted surface is at *rest*, and
collapsing an orthogonal axis into the state map would make `rest`×`pressed`
×`tint` unrepresentable the moment anyone wants a pressed tinted cell.

## The cells

Sized against the calibration doctrine: a fittable set, a validation set, and a
holdout that is never fitted to — and **not** a product tour. Everything is at
1× and at `capsule-button` except where the cell exists precisely to vary that.

2× is deliberately excluded. The tone map is a function of backdrop luminance,
which is scale-free, and W1 measured that every scale-free metric at 2× agrees
with its 1× twin to within noise. The 2× holdout is also already spent.

### `apple-macos-26.5-1x-light-standard` — 12 cells

**Calibration (7)** — the backdrop-luminance sweep is the fit:

| scene id | what it pins |
| --- | --- |
| `dark-solid__capsule-button__rest-tint-orange` | the dark end of the curve (`floor`) |
| `impulse__capsule-button__rest-tint-orange` | near-black with sparse bright energy — separates "dark backdrop" from "dark mean" |
| `checkerboard__capsule-button__rest-tint-orange` | the mid, at maximum local contrast |
| `photo__capsule-button__rest-tint-orange` | the mid, broadband and chromatic |
| `light-solid__capsule-button__rest-tint-orange` | the bright end (`ceilMix`) |
| `photo__capsule-button__rest-tint-blue` | hue independence at the mid |
| `photo__capsule-button__rest-tint-orange-half` | the strength axis |

Five backdrop levels is what fits a two-ended smoothstep with its two edges: four
parameters, five constraints, and the fifth is what makes the fit falsifiable
rather than exact.

**Validation (2)** — checked once, after the fit, before the holdout is opened:

| scene id | what it checks |
| --- | --- |
| `checkerboard__capsule-button__rest-tint-blue` | the second hue away from where it was fitted |
| `photo__rrect-md__rest-tint-orange` | size independence at one step up |

**Holdout (3)** — measured once, reported, never fitted to. The picks follow the
existing holdout reasoning (the axes tuning would most like to peek at):

| scene id | why it is the dangerous one |
| --- | --- |
| `hc-text__capsule-button__rest-tint-orange` | legibility over high-frequency content, which is what tinting most risks |
| `photo__rrect-lg__rest-tint-orange` | the far end of the size axis, where a size-dependent tone would hide |
| `dark-solid__capsule-button__rest-tint-blue` | the second hue at the extreme end of the curve — where a per-hue floor would show and nowhere else |

### `apple-macos-26.5-1x-dark-standard` — 3 cells

`dark-solid`, `checkerboard` and `photo`, capsule, orange. These do not extend
the fit. They answer one question: is the tone curve the same in the dark scheme,
where the *neutral* tint is a different colour? Phase 1 assumes yes (the seed is
the author's, and only the neutral it displaces is scheme-keyed). Three cells
spanning the backdrop range is enough to see the assumption fail.

### The accessibility profiles — 3 cells

macOS couples the toggles, so an increased-contrast capture embodies both flags
(W1's Surprise), and these are two sessions rather than four.

| profile | scenes | what it settles |
| --- | --- | --- |
| `apple-macos-26.5-1x-light-increased-contrast` | `checkerboard` + `photo`, capsule, orange | phase 1 collapses the tone range toward the bare seed on this axis (`ambientTint: "reduced"`). Whether Apple narrows it, drops the tint, or leaves it alone is unmeasured and the two cells decide it. |
| `apple-macos-26.5-1x-light-reduced-transparency` | `photo`, capsule, orange | phase 1 claims this axis touches the tint's *alpha* and not its colour. One cell falsifies that if the colour moves. |

### The total

**18 new native cells**, in four capture sessions (light standard, dark standard,
increased contrast, reduced transparency), one harness rebuild, one TCC re-grant.
The web side measures the same 18 ids on both tiers through the existing compare
path, which is 36 web cells and no new machinery.

If the budget has to shrink, the 12 light-standard cells are the irreducible
core: without the sweep there is no curve, and without the holdout there is no
claim. The dark and accessibility cells test assumptions, and an untested
assumption can be *stated* as one in the claims doc, which is the honest fallback.

## The harness diff, drafted

**Uncommitted on purpose.** `apps/reference-apple/` is not touched by W3 phase 1:
a rebuild invalidates the ad-hoc signature the TCC screen-recording grant is
keyed to, so harness changes batch into a single rebuild the session schedules.
What follows is the whole change, so that rebuild is a paste rather than a design
session.

### `Sources/SceneSpec.swift`

```swift
/// An author tint, as `Glass.tint(_:)` takes it. sRGB components 0…255 and an
/// optional alpha, which is the tint's STRENGTH on both sides: SwiftUI's
/// `Color.opacity` and vitrea's colour-alpha are the same axis.
struct TintSpec: Decodable {
  let srgb: [Int]
  let alpha: Double?

  var color: Color {
    Color(.sRGB,
          red:     Double(srgb[0]) / 255,
          green:   Double(srgb[1]) / 255,
          blue:    Double(srgb[2]) / 255,
          opacity: alpha ?? 1)
  }
}

struct SceneEntry: Decodable {
  let id: String
  let background: String
  let component: String
  let state: String
  /// Absent on every scene that predates W3, which is what keeps the existing
  /// bed byte-identical: no tint declared, no `.tint(_:)` applied.
  let tint: String?
}

// …and on the root spec, beside `backgrounds` and `components`:
//   let tints: [String: TintSpec]?
```

`Color(.sRGB, …)` explicitly rather than `Color(red:green:blue:)`: the whole
pipeline is sRGB-locked (X5) and the capture's observed colour space is
`kCGColorSpaceSRGB`, so the one place a colour enters the native side should name
the space rather than inherit a default.

### `Sources/SceneViews.swift`

```diff
 struct SceneView: View {
   let scene: SceneEntry
   let component: ComponentSpec
   let backgroundImage: CGImage
   let canvas: CGSize
   let pressed: Bool
+  /// Resolved from `scenes.json`'s `tints` registry by the caller; nil for every
+  /// scene that declares none.
+  let tint: Color?

@@
-  /// `interactive()` is what Apple's own controls use for press response, and the
-  /// pressed pose is what the `pressed` scenes measure. It is applied to the
-  /// `Glass` value, not the view — that is the API shape, and it is also why the
-  /// pressed state is a material property here rather than a transform.
+  /// The `Glass` value's non-geometric configuration, in one place.
+  ///
+  /// `interactive()` is what Apple's own controls use for press response, and
+  /// the pressed pose is what the `pressed` scenes measure. `tint(_:)` is the
+  /// same kind of thing — a modifier on the `Glass` value rather than on the
+  /// view — which is exactly why the web side models a tint as material rather
+  /// than as a style on the host element.
   private func material(_ base: Glass = .regular) -> Glass {
-    pressed ? base.interactive(true) : base
+    var glass = pressed ? base.interactive(true) : base
+    if let tint { glass = glass.tint(tint) }
+    return glass
   }
```

`material()` is already called from all three component arms (shape, group,
stack), so nothing else in the file changes — which is the reason the tint went
onto the `Glass` value rather than into each arm.

### `Sources/main.swift`

One resolution at the call site that builds a `SceneView`:

```swift
let tint = scene.tint.flatMap { spec.tints?[$0]?.color }
```

with the same refuse-rather-than-guess posture the rest of the harness takes: a
scene naming a tint id the registry does not hold should be a hard failure at
load, not a silently untinted capture. That failure mode is the one that would
quietly put an untinted cell into a tinted matrix.

### `apps/reference-apple/scenes.json`

The `tints` registry above, 18 scene entries, the split assignments, and the
tinted ids appended to four profiles' `scenes` lists. `light-standard` is
`"scenes": "all"` and picks the new ids up automatically — **which is a trap
worth naming**: it will also try to capture the dark-scheme and accessibility
tinted cells, because "all" means all. Either the tinted ids go into an explicit
list for that profile, or the profile subsets stay as they are and the tinted
cells are declared only where they are wanted. The second is cheaper and matches
how the other five profiles already work.

### The web side

`packages/calibration/scene/` reads the same file and renders through
`GlassSurface`, so the change is one prop: pass `tint` from the resolved scene
entry, formatted as `rgb(r g b / a)` from the same integers the Swift side reads.
Formatting from the *declared integers* rather than from a hex string is what
keeps the two sides on one number.

## The order of operations, when this is scheduled

1. Land the `scenes.json` + Swift diff in **one** harness rebuild, batched with
   whatever else needs one. Re-grant TCC afterwards; capture launches through
   LaunchServices (`open`), never the shell symlink.
2. Capture settled — five minutes after any WindowServer-perturbing event — and
   run the against-committed diff before committing: modified-set
   exactly-as-expected is the gate. The 18 new cells must be *additions*; a
   single byte moving on an existing cell means the harness change was not inert.
3. Measure both tiers through the existing compare path. **Fit once**, on the 7
   calibration cells, against a frozen configuration; check the 2 validation
   cells; then open the holdout **once** and report what it says.
4. If the fit needs a tone curve of a different *shape* — hue-dependent, or
   size-dependent — that is a phase-2 design change, not a retune, and it goes
   back through the wave spec rather than into the constants.
5. The claims doc gains a tint section with its own numbers; both READMEs' "no
   fidelity claim for the author tint" paragraphs are replaced by what was
   measured, and by whatever remains honestly unmeasured.

## What this plan does not cover

- **The `clear` variant tinted.** No canonical scene renders `clear` at all, so a
  tinted clear cell would be the first measurement of two unmeasured things at
  once. Out of scope here for the same reason clear is out of scope generally.
- **Tinted pressed cells.** The native pressed fixtures are byte-identical to
  their rest counterparts (Apple exposes no declarative pressed pose), so a
  tinted pressed cell would measure the rest pose twice.
- **The tone curve under W7's backdrop adaptation.** W7 lands after this and
  changes what the *neutral* tint is per backdrop; the author tint displaces that
  neutral by the author's strength, so the two axes compose by construction. A
  fully-strength tint is unaffected by W7 in either direction, and a partial one
  moves with it. Whether that composition matches Apple needs cells at a partial
  strength over an extreme backdrop — which is W7's measurement to schedule, not
  this one's, and is named here so it is not lost.
