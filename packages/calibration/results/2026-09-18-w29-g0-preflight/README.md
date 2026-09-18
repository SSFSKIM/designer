# W29 G0 — pre-flight on macOS 27, 2026-09-18

Nothing filed, everything attested. The claims section is **c9a §5.149**; the charter is
`docs/doperpowers/specs/2026-09-16-w29-os27-recapture.md`, child G0 (a)–(f).

Raw captures stay on the machine under `~/vitrea-w29-g0-scratch/` (24 runs, 4 dump trees, 3 side
bundles). What is here is derived: the records, the two sheets, and every script that produced them.

| file | what it is |
| --- | --- |
| `machine.json` | (a) the machine, read from the machine and the binary |
| `sdk-gating.json`, `sheets/sdk-gating.png` | (c) the SDK comparison and its verdict |
| `slider-probe.json`, `sheets/slider.png` | (d) `NSGlassTintAmount` against the cells' own run-to-run spread |
| `window-geometry-27.json`, `window-geometry-26.5.json` | (e) the capture region's outer rings, on 27 and on the committed 26.5 fixtures |
| `plan.md` | (f) the eight passes, priced at 10.09 s/cell measured on 27 |
| `bar-table.md` | (f) the 26.5 bar per cell, and the 236 cells that have none |
| `pairs/` | every native-against-native pair the slider probe read |
| `dump-compare-three.json`, `dump-compare-sides.json` | the declared material, bundle against bundle |
| `freeze-verify.txt` | the 26.5 freeze, re-verified after every capture this gate took |

## (a) The machine

macOS **27.0 build 26A428**, Mac14,12 / Apple M2 Pro, kernel 27.0.0. Reduce Transparency **0**,
Increase Contrast **0**, Differentiate Without Color **0**. Xcode **26.6 (17F113)** with
`MacOSX.sdk` at **26.5** (`MacOSX26.sdk` and `MacOSX26.5.sdk` are both symlinks to it); the Command
Line Tools are **27.0.0.0.1788430756**, carry `MacOSX26.5.sdk` and `MacOSX27.0.sdk`, and their
`swiftc` is **Swift 6.4**. The granted bundle's binary reads `minos 26.0`, `sdk 26.0`, cdhash
`88cbbb5b…`, sha256 `bd3092e8…`.

The display is back and is the same screen: persistent id `7709FD0F-F423-4277-B0C8-7CA94F85723A`,
named **`가상 16:9`** by `system_profiler` and by the harness's own `NSScreen.localizedName`, colour
profile **`가상 16:9`** — the same two strings the six 26.5 profiles carry. Mode **68** (2560x1440
scaled, backingScaleFactor 2.0) and mode **69** (2560x1440 unscaled, 1.0) are both present, and both
were reached and left during this gate: the 1x arm of (d) ran under 69 and the display was returned
to 68.

**Two fields are null on purpose.**

*Show Borders.* macOS 27 decouples it from Increase Contrast, and it has **no readable key on this
machine**. `showborders-search.sh` is the search and `showborders-search.txt` its output: all 17
top-level keys of `com.apple.universalaccess` (the same five accessibility booleans 26.5 had, and
nothing border-shaped), the global domain filtered to anything border / glass / tint / contrast /
transparency shaped (only `NSGlassTintAmount`), and `MacOSX27.sdk`'s `NSAccessibility.h`, which
still declares exactly the five `accessibilityDisplayShould…` properties of macOS 10.10–10.12 and
no sixth. What is attested is the **absence of a key**; the setting's state is not readable here,
and under X2 a value nothing can refuse is not an attestation. This needs the user's hand — see the
report.

*The bundle's compiled-against SDK.* `LC_BUILD_VERSION` records `sdk 26.0`, and that figure is
**not** a reading of the SDK that compiled it. `swiftc` links through `clang` with `--sysroot`
rather than `-isysroot`, and clang reads `SDKSettings.plist` only for the latter, so `ld` records
`sdk == minos` whatever SDK was used. Measured: these same sources built against `MacOSX26.5.sdk`
and against `MacOSX27.0.sdk` both came out `sdk 26.0`; forcing the field needs an explicit
`-platform_version`. The charter's Grounding reads the bundle "links the 26.5 SDK … `minos 26.0 sdk
26.0`"; the first half is a build fact (Xcode 26.6's `MacOSX.sdk` is 26.5) and the second is not
evidence for it.

## (b) The granted bundle still captures

Through `open -W`, the way `run-sitting.sh` launches every pass.

- `dump-layers` on `photo__rrect-md__rest`, settle 8: one JSON, **no permission prompt**.
- `capture --scenes photo__rrect-md__rest` into a scratch root: 2 cells across the two 2x standard
  profiles, both `materialRendered: true`, `deterministic: true`, `repeatNoise: 0`,
  `identicalToBackground: false`, `presentedActive: true`. No prompt, no silent denial.
- `deactivate-probe`: the adopted mechanism still reaches the recede —
  `key=false active=false visible=true onscreen=true policy=accessory`, holding after 3 s and after
  an explicit `makeKey()`, and **`SCK ok 640x400`** in that pose, which is the one thing the 26.5
  probe could not close.

## (c) SDK gating — not observed, and the pixel arm needs the user

Three bundles, all `dev.vitrea.reference-apple`, all ad-hoc signed:

| bundle | linked SDK recorded | toolchain | sources | grant |
| --- | --- | --- | --- | --- |
| granted (`build/`) | 26.0 | Xcode 26.6 swiftc 6.3.3, SDK 26.5 | pre-`ee9e7449` | yes |
| side `sdk265` | 26.5 | CLT swiftc 6.4, `MacOSX26.5.sdk` | HEAD | not asked (see below) |
| side `sdk27` | **27.0** | CLT swiftc 6.4, `MacOSX27.0.sdk` | HEAD | **denied, no prompt** |

Xcode 26.6's compiler refuses the 27 SDK outright ("this SDK is not supported by the compiler"), so
one toolchain across both arms is also the only way to hold the compiler fixed while the SDK moves.

**The pixel arm did not run.** `probe` through the `sdk27` side bundle reports
`ScreenCaptureKit: BLOCKED — 사용자가 응용 프로그램, 윈도우, 디스플레이 캡처의 TCC를 거절함`. TCC binds
an ad-hoc signature by its cdhash, a rebuild is a new identity, and a recorded denial suppresses the
prompt. `tccutil reset` was **not** run: it resets by bundle identifier, and the granted bundle
shares that identifier, so it would destroy the wave's one irreplaceable grant. The `sdk265`
control was not probed either, for the same reason in the other direction — each probe writes a TCC
record against its own identity, and the arm that would need the grant is the 27 one.

**The grant-free arm did run, and it is the verdict.** `dump-layers` reads the declared Core
Animation filter tree — the numbers the window server composites from — and needs no grant. On the
charter's cell set (checkerboard capsule, light `hc-text__rrect-sm`, a corner-bearing
`dark-solid__rrect-80`, `photo__rrect-md` in each scheme, and one cell through the `.accessory`
recede):

- `sdk265` against `sdk27`: **9 of 9 cells byte-identical** after the process-local fields are
  dropped — same layer and effect classes, all **81 filter inputs equal**, in both schemes and in
  the recede.
- the granted bundle against both: **8 of 9**. The ninth is the recede arm and its difference is
  the **pose**, not the material: that binary predates `dump-layers --inactive`, ignored the flag
  and presented active, which its own dump records (`isKeyWindow: true`, no `activationPolicy`
  field) and `strings` confirms.

So a binary recording the oldest linked SDK of the three (26.0) declares the same 27 material as
one recording 27.0. The residual is that the window server composites from this tree and could in
principle read the binary's linked SDK itself; only pixels close that, and pixels need the grant.

`sheets/sdk-gating.png` is the granted bundle's own pixels on 27 beside the committed 26.5 fixture
of the same cell. It is **not** the native delta: two axes move between those columns, the OS and
the slider, which did not exist on 26.5. What it shows is that a 26.0-linked binary is plainly not
drawing 26.5's material.

## (d) The slider — it moves every cell, and the centre is 0.5

`NSGlassTintAmount` in `NSGlobalDomain`, a float, found at **0.5459057**, written 2026-09-18 11:59
local. **It drives rendering with no GUI at all**, and it drives it directly: the harness's own
`dump-layers`, relaunched per arm, reports

| key | `inputBlurFillNormalOpacity` | `inputFaceColorMatrixFillColor` alpha | `inputBlurFillLightenOpacity` |
| --- | --- | --- | --- |
| 0.0 | 0 | 0.0000 | 0.675 |
| 0.25 | 0.25 | 0.1000 | 0.7875 |
| 0.5 | 0.5 | 0.2000 | 0.9 |
| 0.5459057 (as found) | 0.545906 | 0.2275 | 0.9 |
| 1.0 | 1 | 0.5000 | 0.9 |
| key deleted | 0.5 | 0.2000 | 0.9 |

The key is the filter input, unrounded. **With the key deleted the material renders at 0.5** — and
0.5 is the knee of both ramps (the face fill's alpha rises 0.0→0.20 over [0, 0.5] and 0.20→0.50
over [0.5, 1.0]; the lighten opacity rises to 0.9 over [0, 0.5] and then holds). So the system's own
default, the value a machine with no key draws, is **0.5**, and this machine is **not at it**.

The pixel arm, three arms over ten cells, three centre runs each as the bar:

| arm | cells | centre run-to-run spread (worst) | 0.0 | 1.0 | 0.5459057 | key deleted |
| --- | ---: | --- | --- | --- | --- | --- |
| 2x active | 6 | maxDelta 2, ΔE 0.006410 | maxDelta 37–74, ΔE ≤ 0.2569 | 60–106, ≤ 0.3566 | 3–12, ≤ 0.0294 | **within the bar** |
| 2x inactive (recede) | 2 | maxDelta 0, ΔE 0 | 34–56, ≤ 0.0849 | 72–103, ≤ 0.2076 | 7–11, ≤ 0.0253 | **byte-identical** |
| 1x active | 2 | maxDelta 0, ΔE 0 | 34–55, ≤ 0.0773 | 62–101, ≤ 0.2088 | 7–12, ≤ 0.0266 | **byte-identical** |

**10 of 10 cells moved beyond their own spread at all three positions, including the as-found
0.5459057** — the 0.046 the machine sits off centre is detectable on every cell of every arm. The
deleted-key arm is inside the spread on every cell, which is the same statement as "absent means
0.5" read from pixels.

By eye (`sheets/slider.png`): at 0.0 the body is nearly clear and the backdrop's structure reads
through it; at 1.0 the light-scheme body washes toward white and the dark-scheme body toward a dark
neutral, so the slider is not a lightness axis but a *material opacity* one, moving each scheme
toward its own tint. The as-found column differs from the centre visibly but faintly. The bar column
is black.

## (e) Window geometry — it does not enter the capture region

The region is the window's own rectangle: borderless, sized to the canvas, `hasShadow = false`,
`SCContentFilter(desktopIndependentWindow:)` with `ignoreShadowsSingleWindow = true`, configuration
width and height the canvas's pixel size and `scalesToFit = false` (`Sources/Capture.swift`).

Measured on the two scenes that would show it first — `rrect-lg`, the largest component the
declaration carries at 280x160 on a 320x200 canvas, and `rrect-80`, plus `toolbar-group` — against
the raster the harness composited into that same window:

- **all four corner pixels of every cell equal the raster exactly**, and the outer ring's minimum
  alpha is **255**. A window clipped to a rounded rectangle composites its corners transparent or
  dark; neither happens.
- the ring differences that do exist are the **component's own** shadow: `rrect-lg` reads ring-1
  worst 7–11 with 530–943 pixels over the noise threshold, and the **committed 26.5 fixtures of the
  same cells read the same pattern** (worst 6–11, 718–975 pixels). `rrect-80` and `toolbar-group`
  read worst 0–1 on both.

No scene's capture region is cut into, and no stop condition fires.

## (f) The plan and the bar table

`plan.md` and `bar-table.md`. In one line each: eight passes, 624 declared cells, **12.24 h at the
seven-run bar** and 15.9–30.6 h with the W27 record's attempt loss, at a measured **10.09 s per
cell** on 27 (26.5 read 9.5 s); and **224 of 619 26.5 cells carry a per-cell bar, 159 more can be
attributed seven only as a group statement, and 236 can be attributed no bar at all**.

## The freeze

`freeze-verify.txt`: **intact, 1,762 entries**, run after every capture this gate took. Nothing
under `apps/reference-apple/fixtures/`, `packages/calibration/profiles/` or `results/matrix.json`
was written; the only reads of `fixtures/` were the manifest and six PNGs, through symlinks, for
(e)'s control and the (c) sheet.
