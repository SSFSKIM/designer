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

/// Which activation pose a run presents its window in.
///
/// Liquid Glass has two appearances and the window server picks between them from
/// the window's key state and the application's active state. Every fidelity claim
/// on the active bed means `.active`. `.inactive` is the window recede W27c
/// measures, and it is a property of the PRESENTATION rather than of the scene:
/// the same view hierarchy, the same raster backdrop and the same `glassEffect`
/// render either pose, so nothing about a scene's content says which one a capture
/// holds. That is exactly why it has to be attested per cell rather than inferred
/// from the scene id — the 121 recovered fixtures are inactive because of how the
/// harness happened to be built in the week they were taken, and no field in the
/// bundle they were written into records it.
enum CapturePose: String, Codable {
  case active
  case inactive
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
  /// Measured 2026-09-11 (macOS 26.5.2 / 25F84): with `keyCapable` false the
  /// window reports exactly the state the recovered bed was taken in, and the
  /// active path is unchanged because `true` is the default and every existing
  /// call site takes it.
  final class CaptureWindow: NSWindow {
    /// Whether AppKit may promote this window to key and main.
    ///
    /// `true` is the active capture pose. `false` is half of the inactive one —
    /// see `presentInactive` — and it is a stored property rather than a second
    /// subclass because the pose has to be a decision the run makes, in one
    /// place, and not a type the rest of the harness has to know about.
    var keyCapable = true
    override var canBecomeKey: Bool { keyCapable }
    override var canBecomeMain: Bool { keyCapable }
  }

  /// A borderless window sized exactly to the canvas, so a window capture needs
  /// no cropping and no titlebar subtraction — both of which are places a
  /// one-pixel offset creeps into every fixture at once.
  @MainActor
  static func makeWindow(canvas: CGSize, keyCapable: Bool = true) -> NSWindow {
    let w = CaptureWindow(contentRect: NSRect(origin: .zero, size: canvas),
                          styleMask: [.borderless], backing: .buffered, defer: false)
    w.keyCapable = keyCapable
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

  /// Put the capture window on screen with the application INACTIVE.
  ///
  /// The exact inverse of `present`, and the three things it inverts are the three
  /// DL14 changes that moved this harness onto the active pose in the first place:
  ///
  ///   1. the process runs under `NSApplication.ActivationPolicy.accessory`
  ///      rather than `.regular` (set before `NSApplication.run`, in `runGUI`);
  ///   2. the capture window answers `false` to `canBecomeKey`/`canBecomeMain`;
  ///   3. nothing on this path calls `activate` — the window is put on screen with
  ///      `orderFrontRegardless()`, which shows a window without activating its
  ///      application, and `makeKey` is never sent.
  ///
  /// **Why this mechanism and not another — measured, not argued.** Run
  /// `./capture.sh deactivate-probe` to reproduce; this is its reading on macOS
  /// 26.5.2 (25F84), Mac14,12, 2026-09-11, with the harness launched the way
  /// `capture.sh` launches it:
  ///
  /// | mechanism | isKeyWindow | NSApp.isActive | on screen | pose |
  /// | --- | --- | --- | --- | --- |
  /// | `.accessory` + `!canBecomeKey` + `orderFrontRegardless`, never activated | false | false | yes | **inactive** |
  /// | `present()` under `.regular` (the active bed) | true | true | yes | active |
  /// | `NSApplication.deactivate()` from the active pose | false | **true** | yes | neither |
  /// | activating another application from the active pose | false | false | yes | inactive |
  ///
  /// `NSApplication.deactivate()` **does not reach the pose on this OS**: the
  /// window resigns key and the application stays active, still after two further
  /// seconds of its own event loop. That is a refutation of the obvious candidate
  /// and not a preference — it is documented as something an application should
  /// not normally call, and here it does half the job.
  ///
  /// Activating some OTHER application — the "second helper process" candidate
  /// `checking-bed.json` names — does reach the pose, and is rejected anyway: it
  /// leaves the run under `.regular`, so the pose is a fact about what happened to
  /// have focus for the next several hours rather than about how the capture was
  /// built, and anything that activates this process puts it back.
  ///
  /// The adopted mechanism holds the pose BY CONSTRUCTION. An `.accessory`
  /// application is not activated by having a window ordered front and has no Dock
  /// tile or menu bar to be activated through; a window whose `canBecomeKey` is
  /// false cannot be promoted by AppKit, and this one ignores mouse events too, so
  /// a stray click reaches neither. Both halves were tested rather than quoted: an
  /// explicit `window.makeKey()` against this configuration left the reading at
  /// `key=false active=false`, and re-entering `.accessory` after a deliberate
  /// activation recovered the pose, so a disturbed session does not have to start
  /// over. It is also the configuration the 121 recovered fixtures were taken
  /// under (the tree before `973fd7e`), which is what makes group E of the
  /// checking bed a re-attestation of the same pose rather than a comparison
  /// against a second, differently-produced one.
  ///
  /// **What the probe could not close.** Whether ScreenCaptureKit returns the
  /// window's pixels while the application is inactive was not read: Screen
  /// Recording is denied to this build on this machine, and TCC is granted per
  /// bundle path, so every fresh build needs it re-granted. The window is
  /// `occlusionState.visible` in the pose, which is the precondition, and the 121
  /// recovered fixtures are SCK captures taken in exactly this configuration —
  /// but that is inference plus history, not a reading. `./capture.sh probe`
  /// answers it in seconds once the grant is in place, and the runbook makes it
  /// the first step of the session.
  ///
  /// Deterministic, but never assumed: the caller attests `isInactivelyPresented`
  /// per cell and refuses to write a fixture without it. This returns after the
  /// state is observed, or throws — a run that cannot reach the pose must stop
  /// before it files a single active pixel under an inactive id.
  /// Asynchronous, and that is a measured requirement rather than a style. The
  /// application's active state is updated by `NSApplication.run` when it
  /// processes an activation EVENT, so a synchronous poll that spins a bare
  /// CFRunLoop reads the state the process started in however long it waits —
  /// measured 2026-09-11 by `deactivate-probe`'s first version, which watched
  /// `occlusionState` change while `NSApp.isActive` stayed stale. Awaiting yields
  /// to AppKit's own loop, which is the only place the answer arrives.
  @MainActor
  static func presentInactive(_ window: NSWindow, settleSeconds: Double = 4.0) async throws {
    if let capture = window as? CaptureWindow, capture.keyCapable {
      throw CaptureError(message: """
        presentInactive: the window was built key-capable. Build it with \
        makeWindow(canvas:keyCapable: false) — a window AppKit may promote to key \
        cannot hold the inactive pose by construction, and this path does not \
        claim a pose it only hopes for.
        """)
    }
    window.orderFrontRegardless()

    // Read after AppKit has had its loop, not on the line after the order-front:
    // activation is the window server's answer, and a reading taken before it
    // answers is a reading of the previous state. Polled so the common case costs
    // one tick and the failure case still ends.
    let deadline = Date().addingTimeInterval(max(0, settleSeconds))
    while !isInactivelyPresented(window) && Date() < deadline {
      try? await Task.sleep(nanoseconds: 100_000_000)
    }
    guard isInactivelyPresented(window) else {
      throw CaptureError(message: """
        presentInactive: the window is \(window.isKeyWindow ? "KEY" : "not key") and \
        the application is \(NSApp.isActive ? "ACTIVE" : "not active") \
        (activation policy \(NSApp.activationPolicy() == .accessory ? "accessory" : "regular")), \
        which is not the inactive pose.

        Both must be false. The usual cause is the process running under the \
        .regular activation policy — `capture --inactive` sets .accessory before \
        NSApplication.run and nothing may call activate afterwards. Run \
        './capture.sh deactivate-probe' to see what this machine does with each \
        mechanism.
        """)
    }
  }

  /// Whether the material is being rendered in its ACTIVE appearance, which is the
  /// one every fidelity claim means. Sampled at capture time rather than assumed.
  @MainActor
  static func isActivelyPresented(_ window: NSWindow) -> Bool {
    window.isKeyWindow && NSApp.isActive
  }

  /// Whether the material is being rendered in its INACTIVE appearance.
  ///
  /// Deliberately NOT `!isActivelyPresented`. That negation is "not (key and
  /// active)", which a window that is key in an inactive app satisfies — and the
  /// recede is the state where BOTH are false. claims §5.134 §5 states the
  /// attestation in exactly those terms, and writing it as a negation of the
  /// active predicate would quietly widen it by one case.
  @MainActor
  static func isInactivelyPresented(_ window: NSWindow) -> Bool {
    !window.isKeyWindow && !NSApp.isActive
  }

  /// Whether a cell captured in `pose` may be WRITTEN, given the three facts that
  /// decide it. Pure, so the rule can be proved without a window — see the
  /// `self-check` subcommand, which runs the whole truth table.
  ///
  /// The screen-lock term is the one that is not obvious, and it is the reason
  /// this is a function rather than two `&&`s at the call site. On a locked screen
  /// nothing can become active or key, so `!isKeyWindow && !appIsActive` — the
  /// inactive attestation — is satisfied **for the wrong reason**, by a session in
  /// which the window server is compositing nothing the bed is about. An inactive
  /// pass that locked mid-run would therefore attest every remaining cell and the
  /// audit would score it perfect. The lock is checked per cell for exactly that
  /// reason: a screen saver or a display sleep after the run's opening gate is the
  /// realistic way it happens, and the opening gate cannot see it.
  static func cellMayBeWritten(pose: CapturePose, isKeyWindow: Bool, appIsActive: Bool,
                               screenLocked: Bool?) -> Bool {
    // `nil` is "the session could not be read", which is not "unlocked" and fails
    // closed, exactly as the idle gate treats an unreadable counter.
    guard screenLocked == false else { return false }
    switch pose {
    case .active: return isKeyWindow && appIsActive
    case .inactive: return !isKeyWindow && !appIsActive
    }
  }

  /// The pose a window is in right now, or `nil` when it is in neither — key in an
  /// inactive application, or not key in an active one. `nil` is a refusal, not a
  /// default: a capture taken in a half-state belongs to no bed.
  @MainActor
  static func observedPose(_ window: NSWindow) -> CapturePose? {
    if isActivelyPresented(window) { return .active }
    if isInactivelyPresented(window) { return .inactive }
    return nil
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
