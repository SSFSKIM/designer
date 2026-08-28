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

/// Set while a capture run holds an unpublished fixture bundle in a staging
/// directory. Every abort goes through `fail`, so this is where the half-written
/// bundle gets removed — the previously committed fixtures and the manifest that
/// describes them are then left exactly as they were.
nonisolated(unsafe) var stagingDirectory: String?

func fail(_ message: String) -> Never {
  if let staging = stagingDirectory {
    try? FileManager.default.removeItem(atPath: staging)
  }
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
  var count = 0

  // No index file: it was keyed by bare id and rewritten wholesale per run, so a
  // run at one scale silently repointed every other scale's consumers at the
  // wrong raster. The manifest's scale-qualified background map is the only
  // lookup now, and every consumer reads it.
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
    count += 1
  }

  print("\(count) backgrounds → \(dir)")
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
  //
  // The split between the two subcommands is deliberate — `backgrounds` needs no
  // window, no permission and no GUI session — so `capture` renders each raster
  // fresh in memory and writes none of them. That leaves one hazard: it records a
  // *path* in the manifest. Change a background definition in scenes.json without
  // re-running `backgrounds`, and the pixels composited here, the file the
  // manifest names, and the file the web calibration page loads are three
  // different images at the same scale, with nothing in the bytes to say so. So
  // capture proves the path it records instead of trusting it.
  var backgroundImages: [String: CGImage] = [:]
  var backgroundFiles: [String: String] = [:]
  for (id, bg) in spec.backgrounds {
    let image = Backgrounds.render(bg, canvas: canvas, scale: scale)
    let relative = "backgrounds/\(id)@\(Int(scale))x.png"

    let onDisk: CGImage
    do { onDisk = try Backgrounds.readPNG(from: "\(root)/\(relative)") }
    catch {
      fail("""
        background '\(id)': \(relative) is missing or unreadable under \(root). \
        capture composites the background it renders in memory and records this \
        path, but only './capture.sh backgrounds' writes the file. Run that at \
        scale \(Int(scale))x first, then re-run capture.
        """)
    }

    let cmp: (mad: Double, maxDelta: Int)
    do { cmp = try Capture.compare(image, onDisk) }
    catch {
      fail("""
        background '\(id)': \(relative) is not the raster this run renders — \
        \(error.localizedDescription). Run './capture.sh backgrounds' at scale \
        \(Int(scale))x first, then re-run capture.
        """)
    }
    guard cmp.maxDelta == 0 else {
      fail("""
        background '\(id)': \(relative) is stale — the committed PNG differs from \
        the raster this run renders (mad=\(cmp.mad), max=\(cmp.maxDelta)). Every \
        fixture would composite pixels that neither the manifest's background path \
        nor the web calibration page loads. Run './capture.sh backgrounds' to \
        regenerate it, then re-run capture.
        """)
    }

    backgroundImages[id] = image
    backgroundFiles[id] = relative
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

  // The bundle is staged, never written in place. `record` writes its PNGs under
  // this directory and `finish` promotes each profile directory and the manifest
  // with an atomic per-path replace.
  //
  // Writing PNGs straight into the final profile directories while the manifest
  // lands only at the very end means a mid-run abort leaves the OLD manifest
  // describing a partly overwritten mix of two runs — worst case, a failed
  // cachedisplay run leaving material-free pixels under a manifest that asserts
  // materialRendered: true, which is exactly the honesty guard this app exists to
  // hold. Staging also means a promoted profile directory replaces its
  // predecessor wholesale, so a profile's files are always the ones its manifest
  // entry describes rather than those plus leftovers from an earlier matrix.
  let staging = "\(root)/.staging-\(UUID().uuidString)"
  do {
    try FileManager.default.createDirectory(atPath: staging, withIntermediateDirectories: true)
  } catch {
    fail("creating the staging directory \(staging): \(error.localizedDescription)")
  }
  stagingDirectory = staging

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

    // The capture model is multi-run by construction — every scale and every
    // accessibility mode needs its own run — so the manifest MERGES: this run's
    // profiles replace same-key entries and every other previously recorded
    // profile is carried forward, so the one manifest.json always describes
    // every fixture directory beside it. Background keys carry the scale
    // ("checkerboard@2x") because a merged manifest spans scales; bare legacy
    // keys are dropped on merge — every post-schema-2 run rewrites its own.
    let scaledBackgrounds = Dictionary(uniqueKeysWithValues:
      backgroundFiles.map { ("\($0.key)@\(Int(backingScale))x", $0.value) })
    var mergedProfiles = profileManifests
    var mergedBackgrounds = scaledBackgrounds
    let rootManifest = URL(fileURLWithPath: "\(root)/manifest.json")
    if let data = try? Data(contentsOf: rootManifest),
       let previous = try? JSONDecoder().decode(FixtureManifest.self, from: data) {
      let capturedKeys = Set(profileManifests.map(\.profileKey))
      mergedProfiles += previous.profiles.filter { !capturedKeys.contains($0.profileKey) }
      for (key, value) in previous.backgrounds
      where key.contains("@") && mergedBackgrounds[key] == nil {
        mergedBackgrounds[key] = value
      }
    }
    mergedProfiles.sort { $0.profileKey < $1.profileKey }

    let manifest = FixtureManifest(
      schemaVersion: 2,
      sceneSpecVersion: spec.version,
      generatedAt: Environment.timestamp(),
      hardware: Environment.hardware(),
      backgrounds: mergedBackgrounds,
      profiles: mergedProfiles,
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
    let stagedManifest = URL(fileURLWithPath: "\(staging)/manifest.json")
    do {
      try enc.encode(manifest).write(to: stagedManifest)
    } catch { fail("writing the staged manifest: \(error.localizedDescription)") }

    // Publish. Profile directories first, the manifest last, each one an atomic
    // replacement of a single path, so the interval in which the bundle could be
    // read half-updated is a handful of renames rather than the whole capture run.
    let fm = FileManager.default
    func promote(_ staged: URL, to published: URL) throws {
      // `replaceItemAt` needs something to replace; a profile captured for the
      // first time has no predecessor, so that case is a plain move.
      if fm.fileExists(atPath: published.path) {
        _ = try fm.replaceItemAt(published, withItemAt: staged)
      } else {
        try fm.moveItem(at: staged, to: published)
      }
    }
    do {
      for p in profileManifests {
        try promote(URL(fileURLWithPath: "\(staging)/\(p.profileKey)"),
                    to: URL(fileURLWithPath: "\(root)/\(p.profileKey)"))
      }
      try promote(stagedManifest, to: URL(fileURLWithPath: "\(root)/manifest.json"))
    } catch {
      fail("publishing the fixture bundle from \(staging): \(error.localizedDescription)")
    }
    try? fm.removeItem(atPath: staging)
    stagingDirectory = nil
    print("manifest → \(root)/manifest.json")

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
  /// Ordered by a stable hash of the cell's own key, which is a permutation by
  /// construction — no stride to be accidentally non-coprime with the matrix
  /// size, and no loop that can fail to terminate. The hash is written out here
  /// rather than using `Hashable`, because Swift's string hashing is seeded per
  /// process: `hashValue` would reorder the matrix on every run, and a capture
  /// order that changes between runs is not comparable between runs.
  func interleaved(_ items: [(ProfileSpec, SceneEntry)]) -> [(ProfileSpec, SceneEntry)] {
    func fnv1a(_ s: String) -> UInt64 {
      var h: UInt64 = 0xcbf2_9ce4_8422_2325
      for byte in s.utf8 {
        h ^= UInt64(byte)
        h = h &* 0x0000_0100_0000_01b3
      }
      return h
    }
    return items.sorted { a, b in
      let ka = fnv1a("\(a.0.key)/\(a.1.id)"), kb = fnv1a("\(b.0.key)/\(b.1.id)")
      // Tie-break on the key itself so the order is total even on a hash collision.
      return ka == kb ? "\(a.0.key)/\(a.1.id)" < "\(b.0.key)/\(b.1.id)" : ka < kb
    }
  }

  // Accessibility modes are system-wide and unsettable per view (see
  // SceneViews.swift). A profile whose key claims a mode the machine is not in
  // would be a mislabelled fixture, so it is skipped rather than captured — and
  // the skip is recorded, because a quietly missing profile is its own kind of lie.
  let systemA11y = SystemAccessibility.current
  // Profile-scoped, not run-scoped: this fact must travel with the fixtures it
  // describes, so it lands on the profile's own manifest entry below.
  let couplingNote: String? =
    (systemA11y == "increased-contrast" && SystemAccessibility.reduceTransparency)
    ? """
      Captured with reduce-transparency also on. That is not contamination: \
      macOS couples the toggles (Increase Contrast force-enables Reduce \
      Transparency, and the transparency checkbox cannot be uncleared while \
      contrast is on — user-verified 2026-08-29), so this is the only reachable \
      increased-contrast state and the one a real user sees.
      """
    : nil
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
  // Fixture directory names and manifest profile keys are `profile.key` verbatim,
  // and the key is where the scale of a fixture is *stated*. Nothing downstream
  // re-measures it, and a PNG carries no record of the scale it was captured at,
  // so capturing a profile whose key claims another scale would mislabel every
  // fixture it writes with no trace in the bytes. Since Wave 1 declared the 2x
  // profiles alongside the 1x ones, the mismatch is a skip-and-record like the
  // accessibility gate above, not a failure: each run captures exactly the
  // profiles whose stated scale is the one this display actually renders, and
  // the run still fails when that leaves nothing.
  let scaleToken = "-\(Int(backingScale))x-"
  let scaleSkipped = Set(work.map { $0.0.key }.filter { !$0.contains(scaleToken) }).sorted()
  work.removeAll { !$0.0.key.contains(scaleToken) }
  if !scaleSkipped.isEmpty {
    caveats.append("""
      Profiles not captured because this display renders at \(backingScale)x and \
      their keys state another scale: \(scaleSkipped.joined(separator: ", ")). A \
      profile is only captured on a display whose backingScaleFactor matches its \
      key — a mismatched run would file \
      \(Int(canvas.width * backingScale))x\(Int(canvas.height * backingScale))-pixel \
      fixtures under a key claiming a different scale, with no trace in the bytes.
      """)
  }
  guard !work.isEmpty else {
    fail("""
      capturing at \(backingScale)x, but no selected profile key says \
      '\(scaleToken)'. Add \(Int(backingScale))x profile entries to scenes.json \
      first — fixture directories and manifest keys are the profile key verbatim.
      """)
  }

  let order = interleaved(work)
  print("capturing \(order.count) fixtures via \(method.rawValue) at \(backingScale)x (interleaved)")

  var byProfile: [String: [FixtureEntry]] = [:]
  /// The colour space the captured images actually carry, per profile. Recorded as
  /// an observation rather than restating the space the capture path requested, so
  /// the manifest field is something a later check can bind against.
  var colorSpaceByProfile: [String: String] = [:]

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
                               // Falls back to the requested space only when the
                               // image reports none at all.
                               colorSpace: colorSpaceByProfile[profile.key] ?? "sRGB",
                               displayName: window?.screen?.localizedName,
                               displayColorProfile: window?.screen?.colorSpace?.localizedName),
          fixtures: entries,
          caveats: profile.a11y == "increased-contrast" ? couplingNote.map { [$0] } : nil))
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

    let dir = "\(staging)/\(profile.key)"
    let file = "\(scene.id).png"

    func record(_ image: CGImage, _ deterministic: Bool?, _ noise: Double?) {
      do { try Backgrounds.writePNG(image, to: "\(dir)/\(file)") }
      catch { fail("writing \(file): \(error.localizedDescription)") }

      colorSpaceByProfile[profile.key] = (image.colorSpace?.name).map { $0 as String } ?? "sRGB"

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
              // The material's tone adaptation is an animation over seconds, and two
              // captures milliseconds apart agree mid-flight — a "byte-stable" reading
              // that is not settled. Measured 2026-08-29: under concurrent system load,
              // individual cells flipped between an adapted and a mid-adaptation byte
              // state across runs (max deltas 31–36/255), while every run's paired
              // captures agreed. Settledness is therefore byte-identity across a real
              // interval: dwell first, then capture at 1s spacing until two consecutive
              // captures agree. The bounded retry keeps a never-settling cell from
              // hanging the run; it records NOISY, which is the honest state.
              try await Task.sleep(nanoseconds: 1_750_000_000)
              var previous = try await Capture.screenCaptureKit(windowID: CGWindowID(w.windowNumber), pixelSize: px)
              var settled = false
              var lastMad = 0.0
              for _ in 0..<7 {
                try await Task.sleep(nanoseconds: 1_000_000_000)
                let next = try await Capture.screenCaptureKit(windowID: CGWindowID(w.windowNumber), pixelSize: px)
                let cmp = try Capture.compare(previous, next)
                lastMad = cmp.mad
                previous = next
                if cmp.maxDelta == 0 { settled = true; break }
              }
              record(previous, settled, settled ? 0 : lastMad)
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
