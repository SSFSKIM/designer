import Foundation
import SwiftUI
import AppKit
import CoreGraphics
import ScreenCaptureKit

/// How a fixture's pixels were obtained. This is a first-class, recorded fact
/// rather than an implementation detail, because on this platform the choice
/// changes *what is in the image* — see `materialRendered`.
enum CaptureMethod: String, Codable {
  /// `SwiftUI.ImageRenderer`. Offscreen and byte-deterministic, and the right
  /// tool for anything that is not glass. It does **not** render Liquid Glass:
  /// measured on macOS 26.5.2 / Xcode 26.6, a `glassEffect` subtree renders as
  /// nothing at all — the material is absent *and* the content it wraps is
  /// dropped.
  case imageRenderer = "swiftui-image-renderer"

  /// `NSView.cacheDisplay(in:to:)` on a live, on-screen window. Renders the view
  /// tree including glass-wrapped *content*, but not the material: the glass body,
  /// its lensing, tint, rim and shadow are all absent.
  case cacheDisplay = "nsview-cachedisplay"

  /// `SCScreenshotManager` against the harness's own window. The only path that
  /// observes the real composited material, because the window server — not the
  /// app — composites it. Requires the Screen Recording TCC grant.
  case screenCaptureKit = "screencapturekit"

  /// Whether this path actually puts Liquid Glass in the image.
  ///
  /// The honest core of this file. A fixture captured by a path that cannot see
  /// the material is still a real capture of a real scene, and it is still useful
  /// for exercising the pipeline — but a fidelity claim built on one would be
  /// measuring the absence of the thing it claims to measure.
  var materialRendered: Bool { self == .screenCaptureKit }
}

struct CaptureError: LocalizedError {
  let message: String
  var errorDescription: String? { message }
}

/// The result of capturing one scene, with the honesty fields attached.
struct CaptureOutcome {
  let image: CGImage
  let method: CaptureMethod
  /// Byte-identical repeat capture? `nil` when determinism was not checked.
  let deterministic: Bool?
  /// Mean absolute RGB difference between two identical captures, 0..255.
  let repeatNoise: Double?
}

enum Capture {

  // MARK: - Offscreen

  @MainActor
  static func imageRenderer(_ view: some View, scale: Double) -> CGImage? {
    let r = ImageRenderer(content: view)
    r.scale = CGFloat(scale)
    r.isOpaque = true
    // sRGB, per X5. ImageRenderer follows the content's colour space; the scenes
    // are authored in sRGB and the raster backgrounds are tagged sRGB, so nothing
    // here widens the gamut.
    return r.cgImage
  }

  // MARK: - Live window

  /// A borderless window that can still become key.
  ///
  /// `NSWindow.canBecomeKey` is documented as "`true` if the window has a title
  /// bar or a resize bar, `false` otherwise" — so the borderless window this
  /// harness needs is, by default, one that can never be key. That is not a
  /// cosmetic detail: Liquid Glass has an active and an inactive appearance, the
  /// window server picks between them from key/active state, and the inactive one
  /// is flat and neutral. Captured through a permanently non-key window, the whole
  /// bed records the material's *unfocused* pose — and an author tint, whose whole
  /// definition is a hue mapped onto a sampled backdrop, has nothing to land on.
  ///
  /// Measured 2026-08-30: before this override the capture window reported
  /// `canBecomeKey: false, isKeyWindow: false, isMainWindow: false,
  /// NSApp.isActive: false`, through every capture of every committed fixture.
  final class CaptureWindow: NSWindow {
    override var canBecomeKey: Bool { true }
    override var canBecomeMain: Bool { true }
  }

  /// A borderless window sized exactly to the canvas, so a window capture needs
  /// no cropping and no titlebar subtraction — both of which are places a
  /// one-pixel offset creeps into every fixture at once.
  @MainActor
  static func makeWindow(canvas: CGSize) -> NSWindow {
    let w = CaptureWindow(contentRect: NSRect(origin: .zero, size: canvas),
                          styleMask: [.borderless], backing: .buffered, defer: false)
    w.isOpaque = true
    w.backgroundColor = .black
    w.hasShadow = false
    // Above normal windows so nothing can occlude the capture, and ignoring mouse
    // events so a stray pointer cannot trigger a hover state mid-matrix.
    w.level = .floating
    w.ignoresMouseEvents = true
    w.center()
    return w
  }

  /// Put the capture window on screen AND make it the key window of an active app.
  ///
  /// Ordering matters and is the reason this is a function rather than two lines at
  /// each call site: a window cannot be key while its application is inactive, so
  /// the app is activated first and the window made key afterwards. The reverse
  /// order — which is what the harness did through every committed capture — leaves
  /// the window ordered front but never key, and Liquid Glass then renders its
  /// inactive, neutral appearance.
  @MainActor
  static func present(_ window: NSWindow) {
    NSApp.activate(ignoringOtherApps: true)
    window.orderFrontRegardless()
    window.makeKeyAndOrderFront(nil)
    window.makeKey()
  }

  /// Whether the material is being rendered in its ACTIVE appearance, which is the
  /// one every fidelity claim means. Sampled at capture time rather than assumed.
  @MainActor
  static func isActivelyPresented(_ window: NSWindow) -> Bool {
    window.isKeyWindow && NSApp.isActive
  }

  @MainActor
  static func cacheDisplay(_ window: NSWindow) throws -> CGImage {
    guard let view = window.contentView,
          let rep = view.bitmapImageRepForCachingDisplay(in: view.bounds) else {
      throw CaptureError(message: "cacheDisplay: no caching representation")
    }
    view.cacheDisplay(in: view.bounds, to: rep)
    guard let image = rep.cgImage else {
      throw CaptureError(message: "cacheDisplay: representation produced no image")
    }
    return image
  }

  /// Capture the harness's own window through ScreenCaptureKit.
  ///
  /// Throws a diagnosable error rather than falling back, because a silent
  /// fallback here is precisely how a material-free image ends up filed as a
  /// material fixture.
  static func screenCaptureKit(windowID: CGWindowID, pixelSize: CGSize) async throws -> CGImage {
    let content: SCShareableContent
    do {
      content = try await SCShareableContent.excludingDesktopWindows(false, onScreenWindowsOnly: true)
    } catch {
      throw CaptureError(message: """
        ScreenCaptureKit is unavailable: \(error.localizedDescription)

        This is the Screen Recording (TCC) gate. Liquid Glass is composited by the
        window server, so no in-process path can observe it — see README.md
        §"The capture wall". Grant Screen Recording to this harness, then re-run.
        """)
    }
    guard let window = content.windows.first(where: { $0.windowID == windowID }) else {
      throw CaptureError(message: "ScreenCaptureKit: the harness window (\(windowID)) is not in the shareable list")
    }
    let filter = SCContentFilter(desktopIndependentWindow: window)
    let cfg = SCStreamConfiguration()
    cfg.width = Int(pixelSize.width)
    cfg.height = Int(pixelSize.height)
    cfg.scalesToFit = false
    cfg.showsCursor = false
    cfg.captureResolution = .best
    cfg.ignoreShadowsSingleWindow = true
    cfg.colorSpaceName = CGColorSpace.sRGB     // X5: sRGB-locked.
    do {
      return try await SCScreenshotManager.captureImage(contentFilter: filter, configuration: cfg)
    } catch {
      throw CaptureError(message: """
        ScreenCaptureKit capture failed: \(error.localizedDescription)

        If this is TCC (-3801), Screen Recording has not been granted to the
        process responsible for this harness. See README.md §"The capture wall".
        """)
    }
  }

  // MARK: - Comparison

  /// Mean absolute RGB difference and the worst channel difference, 0..255.
  ///
  /// Used for the determinism check the child's brief requires: two identical
  /// captures must be byte-stable, or the noise must be documented rather than
  /// averaged away.
  static func compare(_ a: CGImage, _ b: CGImage) throws -> (mad: Double, maxDelta: Int) {
    guard a.width == b.width, a.height == b.height else {
      throw CaptureError(message: "compare: \(a.width)x\(a.height) vs \(b.width)x\(b.height)")
    }
    let pa = try rgba(a), pb = try rgba(b)
    var sum = 0.0
    var maxDelta = 0
    var i = 0
    while i < pa.count {
      for c in 0..<3 {
        let d = abs(Int(pa[i + c]) - Int(pb[i + c]))
        sum += Double(d)
        if d > maxDelta { maxDelta = d }
      }
      i += 4
    }
    return (sum / Double(pa.count / 4 * 3), maxDelta)
  }

  /// How much CHROMA the component added to its own backdrop, over the pixels it
  /// actually changed.
  ///
  /// The tinted-capture attestation's measured half. `TintAttestation` records the
  /// colour handed to `Glass.tint(_:)`; this records whether any colour came out
  /// the other side, and the two together are what make a colourless tint bed
  /// impossible to file silently. A declared hue that composites to a neutral
  /// scrim lands here as ~0 — the same mechanical refusal `identicalToBackground`
  /// offers for an empty capture.
  ///
  /// Per-pixel chroma is `max(r,g,b) - min(r,g,b)`: crude next to a real
  /// colour-appearance model, and deliberately so — it needs no white point, no
  /// gamut and no assumptions, and the question it answers is only "is there any
  /// hue here at all". Measured against the background's OWN chroma at the same
  /// pixels, because a photo backdrop is already colourful and the untinted
  /// material's own desaturation has to be visible as the negative it is.
  ///
  /// Returns nil when the component changed nothing (there is no region to measure).
  static func chromaShift(_ image: CGImage, background: CGImage) throws -> Double? {
    let pa = try rgba(image), pb = try rgba(background)
    guard pa.count == pb.count else {
      throw CaptureError(message: "chromaShift: size mismatch \(pa.count) vs \(pb.count)")
    }
    var sum = 0.0
    var n = 0
    var i = 0
    while i < pa.count {
      let ar = Int(pa[i]), ag = Int(pa[i + 1]), ab = Int(pa[i + 2])
      let br = Int(pb[i]), bg = Int(pb[i + 1]), bb = Int(pb[i + 2])
      // Threshold 2/255, matching the noise floor the repeat-capture check tolerates:
      // below it, "changed" is indistinguishable from capture jitter.
      if abs(ar - br) > 2 || abs(ag - bg) > 2 || abs(ab - bb) > 2 {
        let ac = max(ar, max(ag, ab)) - min(ar, min(ag, ab))
        let bc = max(br, max(bg, bb)) - min(br, min(bg, bb))
        sum += Double(ac - bc)
        n += 1
      }
      i += 4
    }
    return n == 0 ? nil : sum / Double(n)
  }

  /// Decode to straight (non-premultiplied) sRGB RGBA8 — the form the TypeScript
  /// metrics read after a PNG decode, so a comparison made here and a comparison
  /// made there are the same comparison.
  static func rgba(_ image: CGImage) throws -> [UInt8] {
    let w = image.width, h = image.height
    var buf = [UInt8](repeating: 0, count: w * h * 4)
    guard let cs = CGColorSpace(name: CGColorSpace.sRGB) else {
      throw CaptureError(message: "sRGB colour space unavailable")
    }
    let ok: Bool = buf.withUnsafeMutableBytes { raw in
      guard let ctx = CGContext(data: raw.baseAddress, width: w, height: h,
                                bitsPerComponent: 8, bytesPerRow: w * 4, space: cs,
                                bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)
      else { return false }
      ctx.draw(image, in: CGRect(x: 0, y: 0, width: w, height: h))
      return true
    }
    guard ok else { throw CaptureError(message: "rgba: could not create a bitmap context") }
    return buf
  }
}
