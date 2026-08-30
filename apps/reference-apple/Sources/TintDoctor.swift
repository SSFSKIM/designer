import Foundation
import SwiftUI
import AppKit

/// What a tinted capture actually handed to `Glass.tint(_:)`.
///
/// This exists because the W3 tint bed was captured, committed, and only *then*
/// measured — and the measurement found 18 fixtures carrying the tint's strength
/// but not its colour, with nothing in the bundle to say which colour had been
/// applied. A fixture that records the resolved tint beside its pixels can be
/// refused mechanically; one that records only the scene id cannot.
///
/// Every field is an OBSERVATION made at the moment of application, not a restatement
/// of the registry. `declaredSRGB` is what `scenes.json` asked for; `resolvedSRGB` is
/// what SwiftUI's own colour resolution produced from it. When those two disagree,
/// the colour died before the API — and the difference is the evidence.
struct TintAttestation: Codable, Equatable {
  /// The registry id the scene named.
  let tintId: String
  /// What `scenes.json` declared: sRGB 0…255, and alpha-as-strength.
  let declaredSRGB: [Int]
  let declaredAlpha: Double
  /// What `Color.resolve(in:)` produced, in sRGB 0…255 — SwiftUI's own resolution
  /// of the very `Color` value handed to `Glass.tint(_:)`, so a disagreement with
  /// `declaredSRGB` localises the loss to colour construction rather than to the
  /// material.
  let resolvedSRGB: [Double]
  let resolvedOpacity: Double
  /// Does the resolved colour still carry chroma? Max-minus-min across the three
  /// channels, and the boolean the emptiness-style mechanical refusal reads.
  let resolvedChroma: Double
  let colourSurvivedResolution: Bool
  /// Does the `Glass` VALUE distinguish this tint from the same material tinted
  /// with a reference hue? `Glass` is `Equatable`, so this is answerable without
  /// rendering anything: `false` means the colour is already gone inside SwiftUI's
  /// material value, before the window server ever composites it.
  let glassValueDistinguishesHue: Bool

  // The observed half, filled in once the pixels exist. Everything above is
  // knowable before a window opens; everything below needs the capture and the
  // scene's untinted twin, which the interleaved order may capture much later.

  /// `FixtureEntry.chromaShift` of the same scene without its tint, in the same
  /// profile. nil when the bed declares no untinted twin for this scene.
  var untintedTwinChromaShift: Double?
  /// Did any colour actually come out of the material? Compares this capture's
  /// chroma response against that twin's. nil when there was no twin to compare.
  var colourReachedMaterial: Bool?
}

/// Resolution and attestation for one registry tint. One implementation, used by
/// both `tint-doctor` and the capture driver, so the manifest cannot record a
/// different resolution than the doctor reports.
enum TintResolver {

  /// The reference hue the `Glass`-value discrimination test compares against.
  /// Deliberately a colour no registry entry uses, so "equal to the reference"
  /// always means "lost" rather than "coincidentally the same tint".
  static let probeReference = Color(.sRGB, red: 0, green: 1, blue: 0, opacity: 1)

  static func resolved(_ color: Color, colorScheme: ColorScheme = .light) -> Color.Resolved {
    var env = EnvironmentValues()
    env.colorScheme = colorScheme
    return color.resolve(in: env)
  }

  /// Does `Glass.tint(_:)` keep enough of this colour to tell it apart from another
  /// hue at the same alpha? Answered on the `Glass` value itself — no window, no
  /// compositing, no capture permission.
  static func glassDistinguishesHue(_ color: Color) -> Bool {
    let alpha = Double(resolved(color).opacity)
    let reference = probeReference.opacity(alpha)
    return Glass.regular.tint(color) != Glass.regular.tint(reference)
  }

  static func attest(id: String, spec: TintSpec, colorScheme: ColorScheme = .light) -> TintAttestation {
    let color = spec.color
    let r = resolved(color, colorScheme: colorScheme)
    let srgb = [Double(r.red) * 255, Double(r.green) * 255, Double(r.blue) * 255]
    let chroma = (srgb.max() ?? 0) - (srgb.min() ?? 0)
    let declaredChroma = Double((spec.srgb.max() ?? 0) - (spec.srgb.min() ?? 0))
    return TintAttestation(
      tintId: id,
      declaredSRGB: spec.srgb,
      declaredAlpha: spec.alpha ?? 1,
      resolvedSRGB: srgb.map { (($0 * 100).rounded()) / 100 },
      resolvedOpacity: Double(r.opacity),
      resolvedChroma: ((chroma * 100).rounded()) / 100,
      // A declared grey is allowed to resolve grey; a declared hue is not.
      colourSurvivedResolution: declaredChroma < 1 || chroma > declaredChroma * 0.5,
      glassValueDistinguishesHue: glassDistinguishesHue(color))
  }

  /// How much more chroma a tinted capture must show than its untinted twin
  /// before the tint's colour counts as having reached the material, in 0…255
  /// chroma units.
  ///
  /// A threshold is a weaker instrument than the byte-identity test the consumer
  /// side uses (`compare.ts`'s `colourlessTintEvidence`, which refuses a number on
  /// purpose), and it is here for the case byte-identity cannot reach: a bed that
  /// declares only ONE seed per scene has no identical pair to find. The two run
  /// together and the identity test is the one that condemns.
  ///
  /// The value is set from the 2026-08-30 bed's own measurements rather than
  /// chosen: its untinted cells' chroma response spans −3.9…0.0 and its
  /// colourless "tinted" cells span −5.5…+0.4, while the web tier's genuinely
  /// tinted render of the same cells reads +7.7…+34. 1.0 sits an order of
  /// magnitude below the smallest real tint response and clear of the untinted
  /// band's spread — a bed that only just clears it should be looked at, which is
  /// why the failure message prints the number.
  static let chromaResponseFloor = 1.0
}

// MARK: - tint-doctor

/// Report, without capturing anything, exactly what the tinted scenes hand to the
/// Liquid Glass API — and where a lost hue is lost.
///
/// Three probes, each isolating one link in the chain the capture bed measured
/// end-to-end and found broken:
///
///   1. CONSTRUCTION — the `Color` each registry entry builds.
///   2. RESOLUTION   — what SwiftUI's own `Color.resolve(in:)` makes of it, in
///                     both colour schemes, plus AppKit's independent reading.
///   3. MATERIAL     — whether the resulting `Glass` value still tells two hues
///                     apart. `Glass: Equatable` makes this decidable offline,
///                     which is the whole point: it separates "the harness lost
///                     the colour" from "the OS ignores it" with no TCC grant.
@MainActor
func runTintDoctor() {
  let spec = loadSpec()
  guard let tints = spec.tints, !tints.isEmpty else {
    print("scenes.json declares no tints — nothing to diagnose")
    return
  }

  print("== tint doctor ==")
  print("hardware: \(Environment.hardware().model), \(Environment.hardware().osVersion)")
  print("")

  print("-- probe 1/2: Color construction and resolution --")
  for (id, t) in tints.sorted(by: { $0.key < $1.key }) {
    let light = TintResolver.resolved(t.color, colorScheme: .light)
    let dark = TintResolver.resolved(t.color, colorScheme: .dark)
    let ns = NSColor(t.color).usingColorSpace(.sRGB)
    func fmt(_ r: Color.Resolved) -> String {
      String(format: "sRGB(%.1f, %.1f, %.1f) a=%.4f",
             Double(r.red) * 255, Double(r.green) * 255, Double(r.blue) * 255, Double(r.opacity))
    }
    print("  \(id):")
    print("    declared        sRGB(\(t.srgb[0]), \(t.srgb[1]), \(t.srgb[2])) a=\(t.alpha ?? 1)")
    print("    resolved light  \(fmt(light))")
    print("    resolved dark   \(fmt(dark))")
    if let ns {
      print(String(format: "    NSColor sRGB    (%.1f, %.1f, %.1f) a=%.4f  space=%@",
                   ns.redComponent * 255, ns.greenComponent * 255, ns.blueComponent * 255,
                   ns.alphaComponent, ns.colorSpace.localizedName ?? "?"))
    } else {
      print("    NSColor sRGB    UNCONVERTIBLE — the colour has no sRGB reading")
    }
  }

  print("")
  print("-- probe 3: does the Glass VALUE carry the hue? --")
  print("   (Glass is Equatable; two materials tinted with different hues at the same")
  print("    alpha MUST compare unequal if the colour reached the material value)")
  // The control. `!=` is only evidence of discrimination if `==` is reachable at
  // all: a `Glass` equality that never compares two tinted materials equal would
  // make every line below vacuously "YES". Two independently constructed but
  // identical colours must produce equal materials.
  let twin = Color(.sRGB, red: 255 / 255, green: 149 / 255, blue: 0, opacity: 1)
  let twinAgain = Color(.sRGB, red: 255 / 255, green: 149 / 255, blue: 0, opacity: 1)
  print("  CONTROL — same colour, built twice, must be EQUAL: " +
        (Glass.regular.tint(twin) == Glass.regular.tint(twinAgain)
         ? "equal (equality is colour-sensitive, so the answers below mean something)"
         : "UNEQUAL — Glass equality is not value-based; every answer below is vacuous"))
  print("  CONTROL — same hue, different alpha, must be DISTINCT: " +
        (Glass.regular.tint(twin) != Glass.regular.tint(twin.opacity(0.5)) ? "distinct" : "EQUAL"))

  let ids = tints.keys.sorted()
  for id in ids {
    guard let t = tints[id] else { continue }
    let mine = Glass.regular.tint(t.color)
    let vsUntinted = mine != Glass.regular
    let alpha = t.alpha ?? 1
    let vsReference = mine != Glass.regular.tint(TintResolver.probeReference.opacity(alpha))
    print("  \(id): differs from untinted glass: \(vsUntinted ? "YES" : "NO — the tint did not land at all")")
    print("      differs from pure green at the same alpha: " +
          (vsReference ? "YES — the hue is in the material value" : "NO — THE HUE IS GONE INSIDE Glass"))
  }
  // The direct pair the capture bed found byte-identical.
  if let o = tints["orange"], let b = tints["blue"] {
    let equal = Glass.regular.tint(o.color) == Glass.regular.tint(b.color)
    print("  orange vs blue Glass values: \(equal ? "EQUAL — reproduces the byte-identical fixtures" : "DISTINCT")")
  }
  if let o = tints["orange"], let h = tints["orange-half"] {
    let equal = Glass.regular.tint(o.color) == Glass.regular.tint(h.color)
    print("  orange vs orange-half Glass values: \(equal ? "EQUAL" : "DISTINCT — alpha is carried")")
  }

  print("")
  print("-- per-scene: the tint each tinted scene view hands the API --")
  var seen = 0
  for scene in spec.scenes where scene.tint != nil {
    guard let id = scene.tint, let t = spec.tints?[id] else { continue }
    // Resolved through the SAME path `runCapture` uses, so this is not a parallel
    // reimplementation that could agree while the capture path disagrees.
    let a = TintResolver.attest(id: id, spec: t)
    seen += 1
    print("  \(scene.id)")
    print(String(format: "      -> %@ resolved sRGB(%.1f, %.1f, %.1f) a=%.4f chroma=%.1f  colourSurvived=%@ glassKeepsHue=%@",
                 id, a.resolvedSRGB[0], a.resolvedSRGB[1], a.resolvedSRGB[2],
                 a.resolvedOpacity, a.resolvedChroma,
                 a.colourSurvivedResolution ? "yes" : "NO", a.glassValueDistinguishesHue ? "yes" : "NO"))
  }
  print("\n\(seen) tinted scene(s) across \(tints.count) registry entries.")
}
