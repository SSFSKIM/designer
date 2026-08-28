import SwiftUI
import AppKit

/// The native side of the canonical scenes, built on the real Liquid Glass API
/// surface: `glassEffect(_:in:)`, `GlassEffectContainer`, `Glass.interactive()`.
///
/// Two rules shape everything here:
///
/// 1. **The background is an image, never drawn.** Every scene composites the
///    committed raster PNG for its background id. That is the spec's rule
///    ("identical pre-rendered raster backgrounds so font-rasterisation
///    differences never pollute the diff"), and it is also what makes the native
///    and web sides comparable at all.
///
/// 2. **No text inside the glass.** The components are bare material bodies. A
///    label would put a glyph rasteriser — two different ones — inside the region
///    being measured, and the material axis is exactly where that noise would
///    land. Labels are a semantics concern the web side proves separately
///    (parent acceptance #1); they are not part of a material measurement.

struct RasterBackground: View {
  let image: CGImage
  let canvas: CGSize

  var body: some View {
    // `.interpolation(.none)` and an exact frame: the raster is already at capture
    // scale, so any resampling here would blur the very edges the impulse and
    // checkerboard scenes exist to measure.
    Image(decorative: image, scale: image.scale(for: canvas), orientation: .up)
      .interpolation(.none)
      .antialiased(false)
      .frame(width: canvas.width, height: canvas.height)
  }
}

private extension CGImage {
  func scale(for canvas: CGSize) -> CGFloat {
    canvas.width > 0 ? CGFloat(width) / canvas.width : 1
  }
}

/// A shape spec resolved to the SwiftUI shape `glassEffect(in:)` takes.
private func glassShape(_ s: ShapeSpec) -> AnyShape {
  switch s.kind {
  case "capsule": return AnyShape(Capsule())
  case "rrect":
    // `.continuous` is the Apple corner S2 measured (edge reach 1.528665,
    // published as cornerCurveExpansionFactor). Naming it explicitly rather than
    // taking a default is what makes the corner-smoothing seed measurable: the
    // fixture then shows Apple's actual curve, not whichever default the SDK picks.
    return AnyShape(RoundedRectangle(cornerRadius: s.radius ?? 0, style: .continuous))
  default:
    preconditionFailure("unsupported shape kind '\(s.kind)'")
  }
}

/// One scene, ready to render or capture.
struct SceneView: View {
  let scene: SceneEntry
  let component: ComponentSpec
  let backgroundImage: CGImage
  let canvas: CGSize
  let pressed: Bool

  var body: some View {
    ZStack {
      RasterBackground(image: backgroundImage, canvas: canvas)
      componentBody
    }
    .frame(width: canvas.width, height: canvas.height)
    .clipped()
  }

  /// `interactive()` is what Apple's own controls use for press response, and the
  /// pressed pose is what the `pressed` scenes measure. It is applied to the
  /// `Glass` value, not the view — that is the API shape, and it is also why the
  /// pressed state is a material property here rather than a transform.
  private func material(_ base: Glass = .regular) -> Glass {
    pressed ? base.interactive(true) : base
  }

  @ViewBuilder
  private var componentBody: some View {
    switch component {
    case .shape(let s):
      Color.clear
        .frame(width: s.cgSize.width, height: s.cgSize.height)
        .glassEffect(material(), in: glassShape(s))
        .offset(x: s.cgOffset.width, y: s.cgOffset.height)

    case .group(let items, let spacing):
      // One container for the whole row: this is the container-scoped sampling
      // case, and `spacing` is what tells the container how close is close enough
      // to merge. Rendering these as independent surfaces would measure something
      // the spec does not ask about.
      GlassEffectContainer(spacing: spacing) {
        HStack(spacing: spacing) {
          ForEach(Array(items.enumerated()), id: \.offset) { _, item in
            Color.clear
              .frame(width: item.cgSize.width, height: item.cgSize.height)
              .glassEffect(material(), in: glassShape(item))
          }
        }
      }

    case .stack(let base, let over):
      // S1's glass-over-glass scene. The two surfaces are deliberately NOT in one
      // container: the point is that the upper surface samples the lower one's
      // *rendered output*, which is what an overlay plane does. A shared container
      // would union them into a single body and measure the opposite thing.
      ZStack {
        Color.clear
          .frame(width: base.cgSize.width, height: base.cgSize.height)
          .glassEffect(material(), in: glassShape(base))
        Color.clear
          .frame(width: over.cgSize.width, height: over.cgSize.height)
          .glassEffect(material(), in: glassShape(over))
          .offset(x: over.cgOffset.width, y: over.cgOffset.height)
      }
    }
  }
}

/// The appearance environment a profile pins.
///
/// **Only the colour scheme is settable.** `\.colorScheme` is a writable
/// `EnvironmentValues` key, so light and dark profiles can be captured in one run
/// from one process. The accessibility keys are not: on macOS 26.5 /
/// Xcode 26.6, `\.accessibilityReduceTransparency` and
/// `\.accessibilityDifferentiateWithoutColor` are **get-only** — as is
/// `\.colorSchemeContrast` — so `.environment(...)` cannot set them and there is
/// no per-view override of either mode.
///
/// That is a property of the platform, not a gap in this harness, and it has a
/// consequence the manifest has to carry: a `reduced-transparency` or
/// `increased-contrast` profile can only be captured while the *system* is in
/// that mode. `SystemAccessibility` below reads the real state, and the capture
/// driver refuses to write a fixture whose profile key claims a mode the system
/// is not actually in — the alternative is a fixture set that silently says
/// "reduced transparency" about ordinary glass.
extension View {
  @ViewBuilder
  func profileEnvironment(colorScheme: String, a11y: String) -> some View {
    // `a11y` is accepted and ignored on purpose: the parameter documents which
    // profile this view belongs to, and dropping it from the signature would hide
    // that the mode is unsettable here rather than merely unset.
    self.environment(\.colorScheme, colorScheme == "dark" ? .dark : .light)
  }
}

/// The system-wide accessibility display state — the only place these modes live.
enum SystemAccessibility {
  static var reduceTransparency: Bool {
    NSWorkspace.shared.accessibilityDisplayShouldReduceTransparency
  }

  static var increaseContrast: Bool {
    NSWorkspace.shared.accessibilityDisplayShouldIncreaseContrast
  }

  /// The profile a11y token matching the machine's current state.
  ///
  /// Contrast is checked FIRST, and the order is a measurement, not a
  /// preference: on macOS 26.5, turning on Increase Contrast force-enables
  /// Reduce Transparency and the transparency checkbox cannot be uncleared
  /// while contrast is on (user-verified 2026-08-29, Wave 1 / W1). So
  /// (contrast on, transparency off) is unreachable, and the coupled state is
  /// the only increased-contrast state a real user can be in — the
  /// increased-contrast profile therefore captures exactly what a user who
  /// enabled Increase Contrast sees, reduced transparency included. The
  /// capture driver records that coupling as a manifest caveat.
  static var current: String {
    if increaseContrast { return "increased-contrast" }
    if reduceTransparency { return "reduced-transparency" }
    return "standard"
  }
}
