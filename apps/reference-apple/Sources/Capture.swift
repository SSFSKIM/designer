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

  /// A borderless window sized exactly to the canvas, so a window capture needs
  /// no cropping and no titlebar subtraction — both of which are places a
  /// one-pixel offset creeps into every fixture at once.
  @MainActor
  static func makeWindow(canvas: CGSize) -> NSWindow {
    let w = NSWindow(contentRect: NSRect(origin: .zero, size: canvas),
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
