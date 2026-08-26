import Foundation
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

/// Deterministic raster background generation.
///
/// These are drawn with raw CoreGraphics into an sRGB bitmap rather than through
/// SwiftUI, for one reason: SwiftUI's rendering is free to change between OS
/// releases, and a background that shifts is a background that silently
/// invalidates every fixture measured against it. Straight `CGContext` fills of
/// integer-aligned rects, plus arithmetic evaluated per pixel, are reproducible
/// by construction — and the arithmetic ones are specified precisely enough that
/// the web side can regenerate the identical bytes if it ever needs to.
///
/// X5 binds the colour space: sRGB, and only sRGB. The context is created with an
/// explicit sRGB colour space so nothing inherits a display profile.
enum Backgrounds {

  /// Render one background at `scale`, returning an sRGB 8-bit RGBA image.
  static func render(_ spec: BackgroundSpec, canvas: CGSize, scale: Double) -> CGImage {
    let w = Int((canvas.width * scale).rounded())
    let h = Int((canvas.height * scale).rounded())
    let cs = CGColorSpace(name: CGColorSpace.sRGB)!

    switch spec {
    case .syntheticPhoto(let seed):
      // Evaluated per pixel rather than drawn, so the result is a pure function
      // of (x, y, seed) — no rasteriser in the loop at all.
      return perPixel(width: w, height: h, colorSpace: cs) { x, y in
        photoPixel(x: Double(x) / scale, y: Double(y) / scale, seed: seed)
      }

    default:
      // Let CoreGraphics own the backing store (data: nil) — the only reason to
      // hand it our own buffer would be to read the bytes back, and `makeImage`
      // already does that.
      let context = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8,
                              bytesPerRow: w * 4, space: cs,
                              bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
      // Antialiasing off: every edge in these generators is integer-aligned by
      // construction, so AA could only add a half-covered pixel that differs
      // between rasterisers — the one thing a shared background must not do.
      context.interpolationQuality = .none
      context.setAllowsAntialiasing(false)
      context.setShouldAntialias(false)

      draw(spec, into: context, canvas: canvas, scale: scale)
      return context.makeImage()!
    }
  }

  private static func draw(_ spec: BackgroundSpec, into ctx: CGContext, canvas: CGSize, scale: Double) {
    let w = Double(ctx.width), h = Double(ctx.height)

    func fill(_ rgb: [Int], _ rect: CGRect) {
      ctx.setFillColor(red: CGFloat(rgb[0]) / 255, green: CGFloat(rgb[1]) / 255,
                       blue: CGFloat(rgb[2]) / 255, alpha: 1)
      ctx.fill(rect)
    }

    switch spec {
    case .solid(let srgb):
      fill(srgb, CGRect(x: 0, y: 0, width: w, height: h))

    case .checkerboard(let cell, let a, let b):
      let c = cell * scale
      fill(b, CGRect(x: 0, y: 0, width: w, height: h))
      var row = 0
      var y = 0.0
      while y < h {
        var col = 0
        var x = 0.0
        while x < w {
          if (row + col) % 2 == 0 { fill(a, CGRect(x: x, y: y, width: c, height: c)) }
          x += c; col += 1
        }
        y += c; row += 1
      }

    case .impulse(let background, let foreground, let size, let spacing):
      fill(background, CGRect(x: 0, y: 0, width: w, height: h))
      let s = size * scale, gap = spacing * scale
      // Offset by half a period so the grid sits symmetrically inside the canvas
      // and no impulse is clipped — a clipped impulse is not an impulse.
      var y = gap / 2
      while y < h {
        var x = gap / 2
        while x < w {
          fill(foreground, CGRect(x: (x - s / 2).rounded(), y: (y - s / 2).rounded(), width: s, height: s))
          x += gap
        }
        y += gap
      }

    case .textRows(let background, let foreground, let rowHeight, let barHeight):
      fill(background, CGRect(x: 0, y: 0, width: w, height: h))
      let rh = rowHeight * scale, bh = barHeight * scale
      let margin = 12.0 * scale
      var y = margin
      var row = 0
      while y + bh <= h - margin {
        // Deterministic per-row width variation, so the field is not a perfectly
        // periodic grating (which would alias against a blur kernel of the wrong
        // period and give a misleadingly clean measurement).
        let frac = 0.55 + 0.4 * Double((row * 7 + 3) % 10) / 10.0
        let barW = (w - 2 * margin) * frac
        fill(foreground, CGRect(x: margin, y: y, width: barW, height: bh))
        y += rh; row += 1
      }

    case .syntheticPhoto:
      preconditionFailure("synthetic-photo is rendered per pixel, not drawn")
    }
  }

  /// The synthetic photograph: a sum of a few sinusoids per channel.
  ///
  /// Broadband enough to exercise a blur (several octaves present), saturated
  /// enough to exercise tint response, and — the point — a closed-form function
  /// of position, so "identical on both sides" is provable rather than hoped for.
  private static func photoPixel(x: Double, y: Double, seed: Int) -> (UInt8, UInt8, UInt8) {
    // Seed only perturbs phase, so changing it varies the image without changing
    // its statistics.
    let p = Double(seed % 1000) / 1000.0 * 2 * .pi

    func channel(_ k: Double) -> UInt8 {
      let v =
        0.42
        + 0.26 * sin(x / 47.0 + k * 1.7 + p)
        + 0.18 * sin(y / 31.0 - k * 2.3 + p * 0.5)
        + 0.11 * sin((x + y) / 17.0 + k * 0.9)
        + 0.07 * sin((x - 2 * y) / 9.0 - k * 1.1)
        + 0.05 * sin(x / 5.0 + y / 6.0 + k)
      // sRGB-encoded output directly: these are authored values, not the result
      // of light transport, so there is nothing to linearise on the way out.
      return UInt8(max(0, min(255, (v * 255).rounded())))
    }
    return (channel(0), channel(1.9), channel(3.7))
  }

  private static func perPixel(width: Int, height: Int, colorSpace: CGColorSpace,
                               _ f: (Int, Int) -> (UInt8, UInt8, UInt8)) -> CGImage {
    var buf = [UInt8](repeating: 255, count: width * height * 4)
    for y in 0..<height {
      for x in 0..<width {
        let i = (y * width + x) * 4
        let (r, g, b) = f(x, y)
        buf[i] = r; buf[i + 1] = g; buf[i + 2] = b; buf[i + 3] = 255
      }
    }
    let provider = CGDataProvider(data: Data(buf) as CFData)!
    return CGImage(width: width, height: height, bitsPerComponent: 8, bitsPerPixel: 32,
                   bytesPerRow: width * 4, space: colorSpace,
                   bitmapInfo: CGBitmapInfo(rawValue: CGImageAlphaInfo.noneSkipLast.rawValue),
                   provider: provider, decode: nil, shouldInterpolate: false,
                   intent: .defaultIntent)!
  }

  static func writePNG(_ image: CGImage, to path: String) throws {
    let url = URL(fileURLWithPath: path)
    try FileManager.default.createDirectory(at: url.deletingLastPathComponent(),
                                            withIntermediateDirectories: true)
    guard let dst = CGImageDestinationCreateWithURL(
      url as CFURL, UTType.png.identifier as CFString, 1, nil) else {
      throw NSError(domain: "vitrea.png", code: 1,
                    userInfo: [NSLocalizedDescriptionKey: "cannot create PNG destination at \(path)"])
    }
    CGImageDestinationAddImage(dst, image, nil)
    guard CGImageDestinationFinalize(dst) else {
      throw NSError(domain: "vitrea.png", code: 2,
                    userInfo: [NSLocalizedDescriptionKey: "PNG finalize failed for \(path)"])
    }
  }

  /// Read a PNG back. The counterpart to `writePNG`, and the only way to check
  /// that a file on disk is still what the generator produces today — a question
  /// `capture` has to answer, because it composites backgrounds it renders in
  /// memory while recording the path to a file it never writes.
  static func readPNG(from path: String) throws -> CGImage {
    let url = URL(fileURLWithPath: path)
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
      throw NSError(domain: "vitrea.png", code: 3,
                    userInfo: [NSLocalizedDescriptionKey: "no readable PNG at \(path)"])
    }
    return image
  }
}
