import Foundation
import SwiftUI
import AppKit

/// The harness driver.
///
/// Three subcommands, deliberately separable because they have different
/// requirements:
///
///   backgrounds   Generate the shared raster backgrounds. Pure CoreGraphics —
///                 no window, no permission, no GUI session needed.
///   probe         Report what this machine can actually capture, and prove it
///                 by measuring rather than asserting.
///   capture       Render the scene matrix and write fixtures + manifest.
///
/// `capture` takes `--method`, and refuses to guess: a run that cannot use
/// ScreenCaptureKit must be told explicitly to fall back, so a material-free
/// fixture set is always the result of a decision someone made.

let ROOT = URL(fileURLWithPath: #filePath)     // .../Sources/main.swift
  .deletingLastPathComponent()                  // .../Sources
  .deletingLastPathComponent()                  // .../reference-apple
  .path

func fixturesDir() -> String {
  ProcessInfo.processInfo.environment["VITREA_FIXTURES"] ?? "\(ROOT)/fixtures"
}

func fail(_ message: String) -> Never {
  FileHandle.standardError.write(("error: " + message + "\n").data(using: .utf8)!)
  exit(1)
}

func loadSpec() -> SceneSpecFile {
  let path = ProcessInfo.processInfo.environment["VITREA_SCENES"] ?? "\(ROOT)/scenes.json"
  do { return try SceneSpecFile.load(path) }
  catch { fail("cannot load \(path): \(error.localizedDescription)") }
}

/// Capture scale. 1 by default because that is what this machine's display is;
/// overridable so a Retina machine can produce the spec's canonical 2x profiles
/// without editing anything.
func captureScale() -> Double {
  Double(ProcessInfo.processInfo.environment["VITREA_SCALE"] ?? "1") ?? 1
}

// MARK: - backgrounds

func generateBackgrounds() {
  let spec = loadSpec()
  let scale = captureScale()
  let dir = "\(fixturesDir())/backgrounds"
  var written: [String: String] = [:]

  for (id, bg) in spec.backgrounds.sorted(by: { $0.key < $1.key }) {
    let image = Backgrounds.render(bg, canvas: spec.canvas.cgSize, scale: scale)
    let name = "\(id)@\(Int(scale))x.png"
    do { try Backgrounds.writePNG(image, to: "\(dir)/\(name)") }
    catch { fail("writing \(name): \(error.localizedDescription)") }

    // Determinism is cheap to prove here and expensive to discover later.
    let again = Backgrounds.render(bg, canvas: spec.canvas.cgSize, scale: scale)
    let cmp = (try? Capture.compare(image, again)) ?? (mad: -1, maxDelta: -1)
    let mark = cmp.maxDelta == 0 ? "byte-stable" : "UNSTABLE mad=\(cmp.mad) max=\(cmp.maxDelta)"
    print("  \(name)  \(image.width)x\(image.height)  \(mark)")
    written[id] = "backgrounds/\(name)"
  }

  let index = try! JSONSerialization.data(withJSONObject: written, options: [.prettyPrinted, .sortedKeys])
  try? index.write(to: URL(fileURLWithPath: "\(dir)/index.json"))
  print("\(written.count) backgrounds → \(dir)")
}

// MARK: - probe

/// Measure, and report, which capture paths work on this machine.
///
/// This subcommand exists because the answer is not stable across machines or OS
/// versions, and the honest thing for a fidelity harness to do is to state what
/// it verified today rather than what it assumed.
@MainActor
func runProbe() {
  let spec = loadSpec()
  let scale = captureScale()
  let canvas = spec.canvas.cgSize

  guard let bgSpec = spec.backgrounds["checkerboard"],
        let component = spec.components["capsule-button"] else {
    fail("probe needs the checkerboard background and capsule-button component")
  }
  let bg = Backgrounds.render(bgSpec, canvas: canvas, scale: scale)
  let entry = SceneEntry(id: "probe", background: "checkerboard", component: "capsule-button", state: "rest")
  let view = SceneView(scene: entry, component: component, backgroundImage: bg,
                       canvas: canvas, pressed: false)

  print("== capture path probe ==")
  print("hardware: \(Environment.hardware().model), \(Environment.hardware().osVersion)")
  print("requested scale: \(scale)x")

  // Path 1: ImageRenderer, glass on vs a bare rect of the same size. If the
  // material renders, a large region of the image must differ.
  let bare = ZStack {
    RasterBackground(image: bg, canvas: canvas)
    Color.clear.frame(width: 120, height: 44)
  }.frame(width: canvas.width, height: canvas.height)

  if let withGlass = Capture.imageRenderer(view, scale: scale),
     let without = Capture.imageRenderer(bare, scale: scale),
     let cmp = try? Capture.compare(withGlass, without) {
    let expected = 120.0 * 44.0 * scale * scale
    print("ImageRenderer: glass-vs-none mad=\(String(format: "%.4f", cmp.mad)) max=\(cmp.maxDelta) " +
          "(a rendered 120x44 material should move ~\(Int(expected)) px)")
    print("  → material rendered: \(cmp.maxDelta > 0 && cmp.mad > 1.0 ? "PLAUSIBLY YES" : "NO")")
  } else {
    print("ImageRenderer: failed to render")
  }

  // Path 2 and 3 need a live window.
  let window = Capture.makeWindow(canvas: canvas)
  window.contentView = NSHostingView(rootView: view)
  window.makeKeyAndOrderFront(nil)
  NSApp.activate(ignoringOtherApps: true)
  print("window backingScaleFactor: \(window.backingScaleFactor)")

  DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) {
    if let a = try? Capture.cacheDisplay(window), let b = try? Capture.cacheDisplay(window),
       let cmp = try? Capture.compare(a, b) {
      print("cacheDisplay: \(a.width)x\(a.height), repeat mad=\(cmp.mad) max=\(cmp.maxDelta)")
    } else {
      print("cacheDisplay: failed")
    }

    Task { @MainActor in
      let px = CGSize(width: canvas.width * window.backingScaleFactor,
                      height: canvas.height * window.backingScaleFactor)
      do {
        let img = try await Capture.screenCaptureKit(windowID: CGWindowID(window.windowNumber), pixelSize: px)
        print("ScreenCaptureKit: OK \(img.width)x\(img.height) — the material path is available")
      } catch {
        print("ScreenCaptureKit: BLOCKED\n\(error.localizedDescription)")
      }
      NSApp.terminate(nil)
    }
  }
}

// MARK: - capture

@MainActor
func runCapture(method: CaptureMethod) {
  let spec = loadSpec()
  let scale = captureScale()
  let canvas = spec.canvas.cgSize
  let root = fixturesDir()

  // Backgrounds first: every scene composites one, and they must be the same
  // bytes the web side loads.
  var backgroundImages: [String: CGImage] = [:]
  var backgroundFiles: [String: String] = [:]
  for (id, bg) in spec.backgrounds {
    backgroundImages[id] = Backgrounds.render(bg, canvas: canvas, scale: scale)
    backgroundFiles[id] = "backgrounds/\(id)@\(Int(scale))x.png"
  }

  var profileManifests: [ProfileManifest] = []
  var caveats: [String] = []

  // One reusable window for the on-screen paths, so window creation cost and any
  // first-window compositing warm-up do not land on the first scene only.
  let window: NSWindow? = (method == .imageRenderer) ? nil : Capture.makeWindow(canvas: canvas)
  if let w = window {
    w.makeKeyAndOrderFront(nil)
    NSApp.activate(ignoringOtherApps: true)
  }
  let backingScale = Double(window?.backingScaleFactor ?? CGFloat(scale))
  if method != .imageRenderer && backingScale != scale {
    caveats.append("""
      Requested scale \(scale)x but the capture window's backingScaleFactor is \
      \(backingScale)x — this display is not Retina. Fixtures are at \(backingScale)x \
      and their profile keys say so; the spec's canonical 2x profiles cannot be \
      produced on this machine without a HiDPI display mode.
      """)
  }
  if !method.materialRendered {
    caveats.append("""
      captureMethod '\(method.rawValue)' does NOT render the Liquid Glass material. \
      These fixtures contain the scene geometry and background but no glass body, \
      lensing, tint, rim or shadow. They exercise the diff pipeline; they are NOT \
      a fidelity reference and no fidelity claim may cite them.
      """)
  }

  func finish() {
    // The measured emptiness summary. Stated as a count, because "the material
    // did not render" is a claim a reader should be able to check against a number.
    let all = profileManifests.flatMap(\.fixtures)
    let empty = all.filter { $0.identicalToBackground == true }
    if !empty.isEmpty {
      caveats.append("""
        \(empty.count) of \(all.count) fixtures are PIXEL-IDENTICAL to their own \
        background raster: the component contributed no pixels whatsoever. These \
        carry zero information about shape or material and exist only to exercise \
        the diff pipeline end to end.
        """)
    }

    let manifest = FixtureManifest(
      schemaVersion: 1,
      sceneSpecVersion: spec.version,
      generatedAt: Environment.timestamp(),
      hardware: Environment.hardware(),
      backgrounds: backgroundFiles,
      profiles: profileManifests,
      split: .init(calibration: spec.split.calibration,
                   validation: spec.split.validation,
                   holdout: spec.split.holdout,
                   note: """
                     Holdout scene ids are declared here, as data. Tuning code must \
                     read the 'calibration' list; it must never name a holdout scene.
                     """),
      caveats: caveats)

    let enc = JSONEncoder()
    enc.outputFormatting = [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes]
    do {
      try enc.encode(manifest).write(to: URL(fileURLWithPath: "\(root)/manifest.json"))
      print("manifest → \(root)/manifest.json")
    } catch { fail("writing manifest: \(error.localizedDescription)") }

    for c in caveats { print("CAVEAT: \(c)") }
    NSApp.terminate(nil)
  }

  /// The scene list, ordered so the capture methodology interleaves.
  ///
  /// C6 measured GPU clock state moving the same benchmark from 0.995ms to
  /// 1.901ms purely by its slot in the run, and the spec makes interleaving
  /// binding on this child as a result. The same hazard applies to captures: a
  /// material that warms up, or a window server that settles, would otherwise put
  /// a systematic gradient across the matrix in whatever order the scenes happen
  /// to be listed. Interleaving by a fixed stride decorrelates scene identity from
  /// capture position, and the stride is deterministic so a re-run is comparable.
  func interleaved(_ items: [(ProfileSpec, SceneEntry)]) -> [(ProfileSpec, SceneEntry)] {
    guard items.count > 2 else { return items }
    let stride = 7                      // coprime with most matrix sizes here
    var out: [(ProfileSpec, SceneEntry)] = []
    var seen = Set<Int>()
    var i = 0
    while out.count < items.count {
      let idx = i % items.count
      if !seen.contains(idx) { out.append(items[idx]); seen.insert(idx) }
      i += stride
      if seen.count < items.count && i % items.count == 0 { i += 1 }
    }
    return out
  }

  // Accessibility modes are system-wide and unsettable per view (see
  // SceneViews.swift). A profile whose key claims a mode the machine is not in
  // would be a mislabelled fixture, so it is skipped rather than captured — and
  // the skip is recorded, because a quietly missing profile is its own kind of lie.
  let systemA11y = SystemAccessibility.current
  var work: [(ProfileSpec, SceneEntry)] = []
  var skipped: [String] = []
  for profile in spec.profiles {
    guard profile.a11y == systemA11y else {
      skipped.append(profile.key)
      continue
    }
    for scene in spec.scenes(for: profile) { work.append((profile, scene)) }
  }
  if !skipped.isEmpty {
    caveats.append("""
      Profiles not captured because the system is in accessibility mode \
      '\(systemA11y)' and these claim another: \(skipped.joined(separator: ", ")). \
      macOS exposes reduce-transparency and increase-contrast as read-only \
      environment values, so each such profile needs its own run with the \
      corresponding System Settings toggle on (Accessibility > Display).
      """)
  }
  guard !work.isEmpty else {
    caveats.append("No profile matched the system accessibility mode '\(systemA11y)'.")
    finish()
    return
  }
  let order = interleaved(work)
  print("capturing \(order.count) fixtures via \(method.rawValue) at \(backingScale)x (interleaved)")

  var byProfile: [String: [FixtureEntry]] = [:]

  /// Capture one scene, then recurse to the next — the on-screen paths need the
  /// run loop to turn between scenes for the window server to composite the new
  /// content, which a `for` loop would never let happen.
  func step(_ index: Int) {
    guard index < order.count else {
      for profile in spec.profiles {
        let entries = (byProfile[profile.key] ?? []).sorted { $0.sceneId < $1.sceneId }
        guard !entries.isEmpty else { continue }
        profileManifests.append(ProfileManifest(
          profileKey: profile.key,
          colorScheme: profile.colorScheme,
          a11yMode: profile.a11y,
          display: DisplayInfo(requestedScale: scale, actualBackingScale: backingScale,
                               pixelSize: [Int(canvas.width * backingScale), Int(canvas.height * backingScale)],
                               colorSpace: "sRGB"),
          fixtures: entries))
      }
      finish()
      return
    }

    let (profile, scene) = order[index]
    guard let component = spec.components[scene.component],
          let bg = backgroundImages[scene.background],
          let set = spec.split.set(for: scene.id) else {
      fail("scene '\(scene.id)' is not fully resolvable — scenes.json validation should have caught this")
    }

    let view = SceneView(scene: scene, component: component, backgroundImage: bg,
                         canvas: canvas, pressed: scene.state == "pressed")
      .profileEnvironment(colorScheme: profile.colorScheme, a11y: profile.a11y)

    let dir = "\(root)/\(profile.key)"
    let file = "\(scene.id).png"

    func record(_ image: CGImage, _ deterministic: Bool?, _ noise: Double?) {
      do { try Backgrounds.writePNG(image, to: "\(dir)/\(file)") }
      catch { fail("writing \(file): \(error.localizedDescription)") }

      // Measure how much the component actually contributed, rather than assuming
      // it contributed anything.
      let vsBackground = try? Capture.compare(image, bg)
      byProfile[profile.key, default: []].append(FixtureEntry(
        sceneId: scene.id, file: "\(profile.key)/\(file)", fixtureSet: set,
        captureMethod: method.rawValue, materialRendered: method.materialRendered,
        width: image.width, height: image.height,
        deterministic: deterministic, repeatNoise: noise,
        identicalToBackground: vsBackground.map { $0.maxDelta == 0 },
        deltaFromBackground: vsBackground?.mad,
        capturedAt: Environment.timestamp()))

      let d = deterministic.map { $0 ? " byte-stable" : " NOISY(\(noise ?? -1))" } ?? ""
      let e = (vsBackground?.maxDelta == 0) ? " EMPTY(==background)" : ""
      print("  [\(index + 1)/\(order.count)] \(profile.key)/\(scene.id)\(d)\(e)")
    }

    switch method {
    case .imageRenderer:
      guard let a = Capture.imageRenderer(view, scale: scale),
            let b = Capture.imageRenderer(view, scale: scale) else {
        fail("ImageRenderer produced no image for \(scene.id)")
      }
      let cmp = try? Capture.compare(a, b)
      record(a, cmp.map { $0.maxDelta == 0 }, cmp?.mad)
      step(index + 1)

    case .cacheDisplay, .screenCaptureKit:
      guard let w = window else { fail("on-screen capture needs a window") }
      w.contentView = NSHostingView(rootView: view)
      w.displayIfNeeded()
      // Two turns of the run loop plus a short settle: the first lets AppKit lay
      // out the new content, the wait lets the window server composite it. Without
      // it the first capture of each scene is the previous scene's material.
      DispatchQueue.main.asyncAfter(deadline: .now() + 0.25) {
        if method == .cacheDisplay {
          guard let a = try? Capture.cacheDisplay(w), let b = try? Capture.cacheDisplay(w) else {
            fail("cacheDisplay failed for \(scene.id)")
          }
          let cmp = try? Capture.compare(a, b)
          record(a, cmp.map { $0.maxDelta == 0 }, cmp?.mad)
          step(index + 1)
        } else {
          Task { @MainActor in
            let px = CGSize(width: canvas.width * backingScale, height: canvas.height * backingScale)
            do {
              let a = try await Capture.screenCaptureKit(windowID: CGWindowID(w.windowNumber), pixelSize: px)
              let b = try await Capture.screenCaptureKit(windowID: CGWindowID(w.windowNumber), pixelSize: px)
              let cmp = try? Capture.compare(a, b)
              record(a, cmp.map { $0.maxDelta == 0 }, cmp?.mad)
            } catch {
              fail(error.localizedDescription)
            }
            step(index + 1)
          }
        }
      }
    }
  }

  step(0)
}

// MARK: - entry

final class Driver: NSObject, NSApplicationDelegate {
  let action: @MainActor () -> Void
  init(action: @MainActor @escaping () -> Void) { self.action = action }
  func applicationDidFinishLaunching(_ n: Notification) { action() }
}

@main
struct Harness {
  @MainActor
  static func main() {
    let args = Array(CommandLine.arguments.dropFirst())
    let command = args.first ?? "probe"

    switch command {
    case "backgrounds":
      // No GUI needed — and deliberately so, because the shared rasters must be
      // reproducible on a machine with no display session at all.
      generateBackgrounds()

    case "probe":
      runGUI { runProbe() }

    case "capture":
      let raw = value(of: "--method", in: args) ?? "screencapturekit"
      guard let method = CaptureMethod(rawValue: raw) else {
        fail("unknown --method '\(raw)'. One of: " +
             "swiftui-image-renderer, nsview-cachedisplay, screencapturekit")
      }
      runGUI { runCapture(method: method) }

    default:
      fail("usage: harness [backgrounds|probe|capture [--method <m>]]")
    }
  }

  private static func value(of flag: String, in args: [String]) -> String? {
    guard let i = args.firstIndex(of: flag), i + 1 < args.count else { return nil }
    return args[i + 1]
  }

  @MainActor
  private static func runGUI(_ action: @MainActor @escaping () -> Void) {
    let app = NSApplication.shared
    let driver = Driver(action: action)
    app.delegate = driver
    // .accessory rather than .regular: the harness needs a real on-screen window
    // for the capture paths, but it should not steal the Dock or the menu bar
    // while doing it.
    app.setActivationPolicy(.accessory)
    withExtendedLifetime(driver) { app.run() }
  }
}
