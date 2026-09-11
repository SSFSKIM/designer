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

/// The preflight `capture` and `dump-layers` both run before either does
/// anything a refusal would need to undo — writing a fixture, presenting a
/// window, activating the app. `ids` is every scene id this invocation would
/// actually attempt.
///
/// `SceneSpecFile.scenesUnsupportedForFreshCapture` is the pure check; this is
/// just where its answer becomes a refusal, worded once so both call sites say
/// the same thing about the same limitation.
func refuseScenesUnreachableInPose(_ ids: some Sequence<String>, in spec: SceneSpecFile,
                                   pose: CapturePose, remediation: String) {
  let unsupported = spec.scenesUnsupportedForFreshCapture(ids, pose: pose)
  guard !unsupported.isEmpty else { return }
  let why: String
  switch pose {
  case .active:
    why = """
      These declare the window-recede pose (claims §5.128, §5.130). This run \
      presents ACTIVE — Capture.present activates the application and makes the \
      window key — so capturing them here would file active pixels under an \
      inactive id, with nothing in the bytes to say so. The inactive pose has its \
      own run: './capture.sh capture --inactive', which sets the .accessory \
      activation policy before AppKit starts and attests the pose per cell.
      """
  case .inactive:
    why = """
      This run presents INACTIVE — the .accessory activation policy, a window that \
      cannot become key, and no activation on any path — so these 'rest' and \
      'pressed' scenes would be captured in the recede and filed under an active \
      id. The active pose is the ordinary run, without --inactive.
      """
  }
  fail("""
    \(unsupported.count) of the requested scenes declare a state this run's \
    presentation pose cannot reproduce: \(unsupported.joined(separator: ", ")).

    \(why)

    Nothing was captured and no window was opened. \(remediation)
    """)
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
  let entry = SceneEntry(id: "probe", background: "checkerboard", component: "capsule-button",
                         state: "rest", tint: nil, label: nil)
  let view = SceneView(scene: entry, component: component, backgroundImage: bg,
                       canvas: canvas, pressed: false, tint: nil)

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
  Capture.present(window)
  print("window backingScaleFactor: \(window.backingScaleFactor)")

  DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) {
    // Is the capture window KEY? Liquid Glass has an active and an inactive
    // appearance and the window server picks between them; the inactive one is
    // reported flat and neutral, which is the appearance a tint would seem to
    // vanish into. A borderless window returns false from `canBecomeKey` unless a
    // subclass says otherwise, so this is a property of how the window is made
    // rather than of the machine — and it is measurable without capturing.
    print("window canBecomeKey: \(window.canBecomeKey), isKeyWindow: \(window.isKeyWindow), " +
          "isMainWindow: \(window.isMainWindow), NSApp.isActive: \(NSApp.isActive)")

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

// MARK: - rehearse-tints

/// Run the producer-side tint attestation over a fixture bundle that already
/// exists, and report whether a run that produced it would have been refused.
///
/// The check `attestTints` performs is the last thing a capture run does and the
/// most expensive place it can fail: every cell is captured, and then the bundle
/// is thrown away. Whether it will pass is decidable from pixels that are already
/// on disk, so it should never be discovered by spending a session — and it was:
/// the inactive checking bed carries a tinted cell and its untinted twin, and the
/// recede is measured to remove exactly the response the active pose's rule
/// requires.
///
/// This rehearses that rule against a committed bundle with no window, no TCC and
/// no capture. `--pose active` applies the rule as the active bed is held to;
/// `--pose inactive` applies the exemption `TintResolver.attestationMayCondemn`
/// makes. Running both over the recovered inactive fixtures is the proof that the
/// exemption is load-bearing rather than decorative: the first refuses, the second
/// publishes, on the same bytes.
///
/// `Capture.chromaShift` is called here exactly as a run calls it, so this is the
/// same measurement and not a model of it.
func runRehearseTints(pose: CapturePose) {
  let spec = loadSpec()
  let root = fixturesDir()
  let scale = captureScale()
  guard let data = try? Data(contentsOf: URL(fileURLWithPath: "\(root)/manifest.json")),
        let manifest = try? JSONDecoder().decode(FixtureManifest.self, from: data) else {
    fail("rehearse-tints: cannot read \(root)/manifest.json")
  }
  let stateById = Dictionary(uniqueKeysWithValues: spec.scenes.map { ($0.id, $0.state) })
  let backgroundOf = Dictionary(uniqueKeysWithValues: spec.scenes.map { ($0.id, $0.background) })
  // Which scenes DECLARE a tint, from the spec — not which entries recorded an
  // attestation. The recovered inactive bed carries no `tint` field at all (it is
  // 49/334 on the active side and 0/121 on the recovered one), so gating on the
  // recorded field would skip exactly the cells this rehearsal exists to check.
  // A real run attests every scene the spec declares a tint on, so that is the
  // population to rehearse over.
  let tintById = Dictionary(uniqueKeysWithValues:
    spec.scenes.compactMap { scene in scene.tint.map { (scene.id, $0) } })
  func untintedTwinId(of sceneId: String) -> String? {
    let parts = sceneId.components(separatedBy: "__")
    guard parts.count == 3, let marker = parts[2].range(of: "-tint-") else { return nil }
    return "\(parts[0])__\(parts[1])__\(parts[2][..<marker.lowerBound])"
  }

  print("== rehearse-tints ==")
  print("fixtures: \(root)")
  print("pose:     \(pose.rawValue)  (the \(pose == .active ? "active bed's rule" : "recede's exemption"))")
  print("floor:    \(TintResolver.chromaResponseFloor)")
  print("")

  var wouldRefuse: [String] = []
  var checked = 0, exempt = 0
  var cache: [String: CGImage] = [:]
  func image(_ path: String) -> CGImage? {
    if let hit = cache[path] { return hit }
    guard let img = try? Backgrounds.readPNG(from: path) else { return nil }
    cache[path] = img
    return img
  }

  for profile in manifest.profiles.sorted(by: { $0.profileKey < $1.profileKey }) {
    let ids = Set(profile.fixtures.map(\.sceneId))
    for entry in profile.fixtures.sorted(by: { $0.sceneId < $1.sceneId }) {
      guard tintById[entry.sceneId] != nil, let twinId = untintedTwinId(of: entry.sceneId),
            ids.contains(twinId), let background = backgroundOf[entry.sceneId] else { continue }
      let scaleToken = profile.display.actualBackingScale
      guard let bg = image("\(root)/backgrounds/\(background)@\(Int(scaleToken))x.png"),
            let tinted = image("\(root)/\(profile.profileKey)/\(entry.sceneId).png"),
            let plain = image("\(root)/\(profile.profileKey)/\(twinId).png"),
            let own = (try? Capture.chromaShift(tinted, background: bg)) ?? nil,
            let twin = (try? Capture.chromaShift(plain, background: bg)) ?? nil else { continue }
      checked += 1
      let reached = TintResolver.colourReachedMaterial(own: own, untintedTwin: twin)
      // The pose the rehearsal is run under decides which rule applies, so a
      // bundle can be asked both questions. A run applies the scene's own state.
      let condemns = pose == .active ? true
        : TintResolver.attestationMayCondemn(state: stateById[entry.sceneId] ?? "rest")
      if !condemns { exempt += 1 }
      let verdict = reached ? "reached" : (condemns ? "REFUSES THE RUN" : "did not reach — exempt")
      print(String(format: "  %@/%-52@ %9.4f vs twin %9.4f -> %+9.4f  %@",
                   profile.profileKey, entry.sceneId as NSString, own, twin, own - twin, verdict))
      if !reached && condemns { wouldRefuse.append("\(profile.profileKey)/\(entry.sceneId)") }
    }
  }

  print("")
  print("\(checked) tinted cells with an untinted twin; \(exempt) exempt by pose.")
  if wouldRefuse.isEmpty {
    print("This bundle PUBLISHES: no tinted cell condemns the run.")
  } else {
    print("This bundle is REFUSED — \(wouldRefuse.count) cell(s) would fail attestTints():")
    for id in wouldRefuse { print("  \(id)") }
    print("")
    print("A capture run reaching this verdict has already captured every cell.")
    exit(8)
  }
  _ = scale
}

// MARK: - manifest-doctor

/// Decode the committed manifest with today's types, re-encode it, and report
/// every difference.
///
/// Two questions, both of which the repository otherwise answers by argument.
///
/// **Did a schema change move an existing entry?** `FixtureEntry` gained an
/// optional `presentation` for the inactive pose, and an optional that is nil
/// encodes to nothing — so an active entry must survive this round trip
/// byte-identically. "Must" is worth a program rather than a sentence, because the
/// committed bundle is the provenance every fidelity claim rests on.
///
/// **What would a merge silently drop?** `capture` carries forward the profiles it
/// did not capture by DECODING them into these types and re-encoding them, so any
/// field the committed manifest holds and `FixtureEntry` does not declare is lost
/// on the next run that touches the same fixture root. That is how evidence
/// disappears without a diff anyone reads, and naming the fields is the only way to
/// keep the loss from being discovered by its consequences.
///
/// Reads one file and writes nothing.
func runManifestDoctor() {
  let path = "\(fixturesDir())/manifest.json"
  guard let data = try? Data(contentsOf: URL(fileURLWithPath: path)) else {
    fail("manifest-doctor: cannot read \(path)")
  }
  guard let decoded = try? JSONDecoder().decode(FixtureManifest.self, from: data) else {
    fail("manifest-doctor: \(path) does not decode with today's types at all")
  }
  let enc = JSONEncoder()
  enc.outputFormatting = [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes]
  guard let round = try? enc.encode(decoded),
        let before = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
        let after = try? JSONSerialization.jsonObject(with: round) as? [String: Any] else {
    fail("manifest-doctor: could not re-encode")
  }

  func fixtures(_ manifest: [String: Any]) -> [String: [String: Any]] {
    var out: [String: [String: Any]] = [:]
    for profile in (manifest["profiles"] as? [[String: Any]] ?? []) {
      let key = profile["profileKey"] as? String ?? "?"
      for entry in (profile["fixtures"] as? [[String: Any]] ?? []) {
        out["\(key)/\(entry["sceneId"] as? String ?? "?")"] = entry
      }
    }
    return out
  }
  let old = fixtures(before), new = fixtures(after)
  print("== manifest-doctor ==")
  print("file: \(path)")
  print("entries: \(old.count) before, \(new.count) after a decode/encode round trip")

  var lostFields: [String: Int] = [:]
  var changedValues: [String] = []
  var identical = 0
  for (cell, was) in old {
    guard let now = new[cell] else { lostFields["<the whole entry>", default: 0] += 1; continue }
    var differs = false
    for (field, value) in was {
      guard let carried = now[field] else {
        lostFields[field, default: 0] += 1
        differs = true
        continue
      }
      if !NSDictionary(dictionary: [field: value]).isEqual(to: [field: carried]) {
        changedValues.append("\(cell).\(field)")
        differs = true
      }
    }
    for field in now.keys where was[field] == nil {
      changedValues.append("\(cell).\(field) ADDED")
      differs = true
    }
    if !differs { identical += 1 }
  }

  // "Round-trips with no field lost and no value changed" — NOT byte-identity.
  // The comparison is over parsed values, so key order and float formatting are
  // normalised away by construction. That is the right comparison for the two
  // questions this asks (did a schema change move an entry; what would a merge
  // drop), and claiming more than it checks would be the same class of error it
  // exists to catch.
  print("\n\(identical) of \(old.count) entries round-trip with NO FIELD LOST AND NO VALUE")
  print("CHANGED. Parsed values are compared, so key order and number formatting are")
  print("normalised away; this is not a byte comparison of the two encodings.")
  if lostFields.isEmpty {
    print("No field is dropped: today's types describe everything in this file.")
  } else {
    print("\nDROPPED by the round trip — a merge that carries an untouched profile")
    print("forward re-encodes it through these types, so these fields are lost:")
    for (field, n) in lostFields.sorted(by: { $0.key < $1.key }) {
      print("  \(field)  on \(n) entries")
    }
    print("\nThis is why `capture --scenes` and `capture --inactive` refuse a fixture")
    print("root that already holds a manifest. Raw runs go to their own root and")
    print("`materialize` publishes from them; nothing merges into the bundle in place.")
  }
  if !changedValues.isEmpty {
    print("\nVALUES CHANGED (this is a schema fault, not a merge hazard):")
    for change in changedValues.sorted().prefix(40) { print("  \(change)") }
    if changedValues.count > 40 { print("  … and \(changedValues.count - 40) more") }
  }
}

// MARK: - deactivate-probe

/// Measure what each candidate deactivation mechanism actually does on THIS
/// machine, and whether the window stays capturable while it is inactive.
///
/// `presentInactive` picks one mechanism and says why; this is where the "why"
/// is a reading rather than an argument. It exists for the same reason `probe`
/// does: the answer is not stable across machines or OS versions, and the honest
/// thing for a fidelity harness to do is state what it verified today.
///
/// Nothing is captured to disk and no fixture, scene or manifest is touched. The
/// one ScreenCaptureKit call per arm is the question "can the window server still
/// see this window while the app is inactive" — which is the half of the
/// mechanism that AppKit's own state flags cannot answer — and its image is
/// measured in memory and dropped. The mean-absolute difference it prints between
/// the active and inactive arms is a DIAGNOSTIC that the pose changed the pixels
/// at all; it is written nowhere, it is not a reading of Apple's material, and no
/// claim may cite it.
@MainActor
func runDeactivateProbe() {
  let spec = loadSpec()
  let scale = captureScale()
  let canvas = spec.canvas.cgSize
  setvbuf(stdout, nil, _IOLBF, 0)

  guard let bgSpec = spec.backgrounds["checkerboard"],
        let component = spec.components["capsule-button"] else {
    fail("deactivate-probe needs the checkerboard background and capsule-button component")
  }
  let bg = Backgrounds.render(bgSpec, canvas: canvas, scale: scale)
  let entry = SceneEntry(id: "probe", background: "checkerboard", component: "capsule-button",
                         state: "rest", tint: nil, label: nil)
  let view = SceneView(scene: entry, component: component, backgroundImage: bg,
                       canvas: canvas, pressed: false, tint: nil)
    .profileEnvironment(colorScheme: "light", a11y: "standard")

  print("== deactivate-probe ==")
  print("hardware: \(Environment.hardware().model), \(Environment.hardware().osVersion) " +
        "(\(Environment.hardware().osBuild))")
  print("launch activation policy: \(NSApp.activationPolicy() == .accessory ? "accessory" : "regular")")
  let locked = Environment.screenIsLocked()
  print("screen locked: \(locked.map(String.init(describing:)) ?? "unreadable")")
  if locked != false {
    print("")
    print("NOTE: on a locked screen nothing can become active or key, so EVERY arm below")
    print("reads `inactive` and the contrast arms measure nothing. `onscreen` (the window's")
    print("occlusionState) also reads false while locked. Unlock the console session before")
    print("believing any row here.")
  }
  print("")

  /// One reading of the state the attestation is made of.
  func state(_ label: String, _ window: NSWindow) -> String {
    func pad(_ s: String, _ n: Int) -> String {
      s.count >= n ? s : s + String(repeating: " ", count: n - s.count)
    }
    func flag(_ b: Bool) -> String { pad(b ? "true" : "false", 5) }
    let policy = NSApp.activationPolicy() == .accessory ? "accessory" : "regular"
    let pose = Capture.observedPose(window).map(\.rawValue) ?? "NEITHER"
    return "  \(pad(label, 30)) key=\(flag(window.isKeyWindow)) active=\(flag(NSApp.isActive)) " +
           "visible=\(flag(window.isVisible)) onscreen=\(flag(window.occlusionState.contains(.visible))) " +
           "policy=\(pad(policy, 9)) -> \(pose)"
  }

  Task { @MainActor in
    /// Yield to AppKit's own event loop for a while.
    ///
    /// `await` and not `RunLoop.run(mode:before:)`, and the difference is the
    /// whole reason this probe exists rather than a paragraph of reasoning.
    /// Activation state arrives as an AppKit event, so it is `NSApplication.run`
    /// that updates `isActive` — spinning a bare CFRunLoop pumps the window
    /// server's compositing (measured: `occlusionState` moved) while leaving
    /// `NSApp.isActive` on its stale value, so a poll written that way reports the
    /// pose it started in no matter what the mechanism did.
    func settle(_ seconds: Double) async {
      try? await Task.sleep(nanoseconds: UInt64(max(0, seconds) * 1_000_000_000))
    }

    var images: [String: CGImage] = [:]

    /// Ask ScreenCaptureKit for the window, in memory, and drop it. This is the
    /// reading AppKit cannot give: a window can report visible and still not be in
    /// the shareable list, and a bed cannot be captured through a window that is not.
    @MainActor func shareable(_ window: NSWindow, arm: String) async -> String {
      let px = CGSize(width: canvas.width * window.backingScaleFactor,
                      height: canvas.height * window.backingScaleFactor)
      do {
        let image = try await Capture.screenCaptureKit(
          windowID: CGWindowID(window.windowNumber), pixelSize: px)
        images[arm] = image
        return "SCK ok \(image.width)x\(image.height)"
      } catch {
        return "SCK FAILED — \(error.localizedDescription.prefix(120))"
      }
    }

    // Each arm is measured under the activation policy it describes, and a
    // process has exactly one launch policy — so the probe runs twice. Under
    // `.accessory` it measures the ADOPTED mechanism, which is defined by the
    // policy never having been `.regular`; under `.regular` it measures the
    // active pose and the two rejected candidates, which all start from it.
    //
    // Measured 2026-09-12, after a first version flipped the policy mid-run: a
    // process launched `.accessory` cannot be made `.regular` and active again on
    // this OS, so the contrast arms read `inactive` there and would have reported
    // the active pose as the recede. An arm measured under the wrong launch
    // configuration is worse than an arm not measured.
    let launched = NSApp.activationPolicy()
    if launched == .accessory {
      let inactive = Capture.makeWindow(canvas: canvas, keyCapable: false)
      inactive.contentView = NSHostingView(rootView: view)
      print("A. .accessory + !canBecomeKey + orderFrontRegardless, never activated  [ADOPTED]")
      print("     policy set before NSApplication.run, as `capture --inactive` sets it")
      inactive.orderFrontRegardless()
      await settle(1.2)
      print(state("after orderFrontRegardless", inactive))
      await settle(3.0)
      print(state("3s later (does it hold?)", inactive))
      print("     \(await shareable(inactive, arm: "inactive"))")
      // The one call that could break it, asked for on purpose, because "cannot
      // become key" has to be tested rather than quoted from a header.
      inactive.makeKey()
      await settle(0.8)
      print(state("after an explicit makeKey()", inactive))
      print("")
      print("Arms B-E start from the active pose and need the other launch policy:")
      print("  ./capture.sh deactivate-probe --launch regular")
    } else {
      // ARM B — the active pose, as every committed active fixture was taken.
      let active = Capture.makeWindow(canvas: canvas)
      active.contentView = NSHostingView(rootView: view)
      Capture.present(active)
      await settle(1.2)
      print("B. present() under .regular  [the active pose, DL14's three changes]")
      print(state("after present", active))
      print("     \(await shareable(active, arm: "active"))")

      // ARM C — NSApp.deactivate() from that state.
      NSApp.deactivate()
      await settle(1.2)
      print("C. NSApp.deactivate()        [candidate: documented as 'do not normally call']")
      print(state("after deactivate", active))
      await settle(2.0)
      print(state("2s later (does it hold?)", active))

      // ARM D — activate another application, the candidate checking-bed.json names.
      Capture.present(active)
      await settle(0.8)
      let other = NSWorkspace.shared.runningApplications.first {
        $0.activationPolicy == .regular
          && $0.processIdentifier != ProcessInfo.processInfo.processIdentifier
          && $0.bundleIdentifier != nil
      }
      if let other {
        _ = other.activate(options: [])
        await settle(1.5)
        print("D. activate another app      [candidate: 'a second helper process', "
              + "\(other.bundleIdentifier ?? "?")]")
        print(state("after other.activate", active))
      } else {
        print("D. activate another app      — no other .regular application is running")
      }
      active.orderOut(nil)

      // ARM E — can the pose be RECOVERED after an activation? This is the case a
      // mid-run mistake lands in, and the answer decides whether a disturbed
      // session has to start over.
      _ = NSApp.setActivationPolicy(.accessory)
      await settle(1.5)
      let again = Capture.makeWindow(canvas: canvas, keyCapable: false)
      again.contentView = NSHostingView(rootView: view)
      again.orderFrontRegardless()
      await settle(2.0)
      print("E. back to .accessory after an activation  [is the pose recoverable?]")
      print(state("after re-entering accessory", again))
    }

    if let a = images["active"], let b = images["inactive"], let cmp = try? Capture.compare(a, b) {
      print("")
      print(String(format: "DIAGNOSTIC (written nowhere, not a reading of the material): " +
                   "active vs inactive mad=%.4f max=%d", cmp.mad, cmp.maxDelta))
    }
    print("")
    print("Nothing was captured to disk. No fixture, scene or manifest was touched.")
    NSApp.terminate(nil)
  }
}

// MARK: - dump-layers

/// The scenes whose layer trees are worth reading by default.
///
/// A complete span column first, because the material's size law is the one
/// thing the calibration bed fits that a single scene cannot distinguish: if
/// Apple's filter carries a span-dependent blur radius or refraction height, it
/// is visible only as a column of numbers across ascending spans. That column is
/// taken on `checkerboard`, which is the only background carrying all four
/// rrect sizes — `light-solid` declares no `rrect-sm` or `rrect-lg` — and the
/// two `light-solid` cells that do exist are dumped beside it so that a
/// parameter which is a property of the *material* rather than of the backdrop
/// can be told from one that is not. The rest add one variable each — a merged
/// container, a surface sampling another surface, the pressed pose, an author
/// tint — so anything that moves can be attributed to the variable that moved it.
let DUMP_LAYER_DEFAULT_SCENES = [
  "checkerboard__rrect-sm__rest",
  "checkerboard__capsule-button__rest",
  "checkerboard__rrect-md__rest",
  "checkerboard__rrect-ml__rest",
  "checkerboard__rrect-lg__rest",
  "light-solid__capsule-button__rest",
  "light-solid__rrect-md__rest",
  "light-solid__rrect-ml__rest",
  "checkerboard__toolbar-group__rest",
  "photo__glass-over-glass__rest",
  "checkerboard__rrect-md__pressed",
  "photo__capsule-button__rest-tint-orange",
]

/// Dump the Core Animation layer tree SwiftUI commits for each scene.
///
/// The window is real, presented and key, and the run waits before reading:
/// `glassEffect` does not build its backdrop layer, its filter or its SDF
/// elements until SwiftUI has committed the hosting view's layer tree and Core
/// Animation has run a transaction over it, so a walk taken immediately after
/// `contentView` is assigned finds a bare hosting layer with nothing under it.
/// The window must also be key for the same reason `capture` insists on it —
/// the inactive appearance is a different material and would be a different set
/// of numbers.
///
/// Nothing is captured, nothing is written under `fixtures/`, and `scenes.json`
/// is read exactly as `capture` reads it so the scene ids mean the same thing in
/// both places.
@MainActor
func runDumpLayers(sceneIds: [String], outDir: String, settleSeconds: Double, scheme: String?) {
  let spec = loadSpec()
  let scale = captureScale()
  let canvas = spec.canvas.cgSize

  // A dump never lands under `fixtures/`. It cannot today — the default is
  // `build/layer-dumps` and `--out` is a path the caller names — but `--out` is a
  // path the caller names, and the one rule that makes the fixture bed
  // trustworthy is worth a check rather than a convention. A labelled probe
  // scene is exactly the case where a mistyped `--out` would matter.
  let fixtures = URL(fileURLWithPath: fixturesDir()).standardizedFileURL.path
  let resolved = URL(fileURLWithPath: outDir).standardizedFileURL.path
  if resolved == fixtures || resolved.hasPrefix(fixtures + "/") {
    fail("""
      --out \(outDir) is inside the fixture directory \(fixtures). A layer dump is \
      not a fixture and nothing this subcommand writes may live beside the bed — \
      see SceneViews.swift's rule 2, which is why a labelled scene can be dumped \
      at all. Nothing was written and no window was opened.
      """)
  }

  let byId = Dictionary(uniqueKeysWithValues: spec.scenes.map { ($0.id, $0) })
  var wanted: [SceneEntry] = []
  for id in sceneIds {
    guard let scene = byId[id] else { fail("no scene '\(id)' in the loaded spec") }
    wanted.append(scene)
  }

  do {
    try FileManager.default.createDirectory(atPath: outDir, withIntermediateDirectories: true)
  } catch {
    fail("creating \(outDir): \(error.localizedDescription)")
  }

  // The light profile's environment, which is what every default scene here is
  // authored against. The dump reads a configuration, not a rendering, so there
  // is no reason to walk both schemes unless a question asks for it — and a
  // `--scenes` list is free to name a scene of either kind, which then gets this
  // same environment and says so in the file it writes.
  // `--scheme` exists because claims §5.133 §6 records scheme, scale and
  // accessibility as FULLY CONFOUNDED in the committed corpus — 57 of 57 dumps are
  // light, 1x, standard — so "does the dark scheme carry a third operator" is a
  // question no amount of re-reading the corpus can answer and one flag can.
  let wantedScheme = scheme ?? "light"
  guard wantedScheme == "light" || wantedScheme == "dark" else {
    fail("--scheme takes 'light' or 'dark', not '\(wantedScheme)'")
  }
  let profile = spec.profiles.first { $0.colorScheme == wantedScheme && $0.a11y == "standard" }
  let colorScheme = profile?.colorScheme ?? wantedScheme
  let a11y = profile?.a11y ?? "standard"

  // Line-buffered: this subcommand is normally run through `open --stdout <log>`,
  // where a block-buffered stdout means a run that hangs leaves an empty file and
  // no way to tell how far it got.
  setvbuf(stdout, nil, _IOLBF, 0)

  let window = Capture.makeWindow(canvas: canvas)
  Capture.present(window)
  print("== dump-layers ==")
  print("hardware: \(Environment.hardware().model), \(Environment.hardware().osVersion)")
  print("window backingScaleFactor: \(window.backingScaleFactor), isKeyWindow: \(window.isKeyWindow), " +
        "NSApp.isActive: \(NSApp.isActive)")
  print("environment: colorScheme=\(colorScheme) a11y=\(a11y) (system a11y: \(SystemAccessibility.current))")
  print("out: \(outDir)")

  Task { @MainActor in
    for scene in wanted {
      guard let component = spec.components[scene.component],
            let bgSpec = spec.backgrounds[scene.background] else {
        fail("scene '\(scene.id)' is not fully resolvable")
      }
      let bg = Backgrounds.render(bgSpec, canvas: canvas, scale: scale)
      let tint = scene.tint.flatMap { spec.tints?[$0]?.color }
      let view = SceneView(scene: scene, component: component, backgroundImage: bg,
                           canvas: canvas, pressed: scene.state == "pressed", tint: tint,
                           label: scene.label)
        .profileEnvironment(colorScheme: colorScheme, a11y: a11y)
      window.contentView = NSHostingView(rootView: view)
      window.displayIfNeeded()

      // The commit that materialises the glass layers happens off this call
      // stack and there is no notification to wait on, so the only honest thing
      // to do is wait longer than it takes and say so. It has to be longer than
      // the material's own settling too: several of the filter's inputs are
      // animated in when the surface appears, and a dump taken too early records
      // a frame of that animation as if it were the material. `--settle` exists
      // so the question "are these numbers settled?" can be answered by asking
      // twice rather than by assuming.
      try? await Task.sleep(nanoseconds: UInt64(max(0, settleSeconds) * 1_000_000_000))

      guard let root = window.contentView else { fail("scene '\(scene.id)': the window has no content view") }
      var record: [String: Any] = [
        "scene": scene.id,
        "background": scene.background,
        "component": scene.component,
        "state": scene.state,
        "tint": scene.tint ?? NSNull(),
        // Recorded so a reader can tell a labelled dump from its bare twin
        // without re-deriving it from the scene id, and so the label's declared
        // colour travels with the matrices it may or may not have produced.
        "label": scene.label.map { label -> [String: Any] in
          var out: [String: Any] = ["text": label.text, "fontSize": label.fontSize ?? 15]
          out["srgb"] = label.srgb ?? NSNull()
          return out
        } ?? NSNull(),
        "colorScheme": colorScheme,
        "a11y": a11y,
        "canvas": ["width": canvas.width, "height": canvas.height],
        "backingScaleFactor": Double(window.backingScaleFactor),
        "settleSeconds": settleSeconds,
        "isKeyWindow": window.isKeyWindow,
        "os": Environment.hardware().osVersion,
      ]
      record["view"] = LayerDump.describeView(root)

      print("\n--- \(scene.id) ---")
      LayerDump.printSummary(record)

      let path = "\(outDir)/\(scene.id).json"
      do {
        let data = try JSONSerialization.data(withJSONObject: record,
                                              options: [.prettyPrinted, .sortedKeys])
        try data.write(to: URL(fileURLWithPath: path))
        print("  → \(path)")
      } catch {
        // A scene whose tree holds something JSONSerialization will not take is
        // a finding, not a reason to lose the other nine dumps.
        print("  ! could not write \(path): \(error.localizedDescription)")
      }
    }
    print("\ndone: \(wanted.count) scenes → \(outDir)")
    NSApp.terminate(nil)
  }
}

// MARK: - capture

/// The protocol knobs a stability study needs, and a normal capture leaves alone.
///
/// Defaults reproduce the capture every committed bed was taken under, so a run
/// with no study flags is the same run it always was.
struct CaptureOptions {
  var runLabel: String?
  /// Permutes the capture order. Absent keeps the fixed stable order, which is
  /// what makes two ordinary runs comparable — see `interleaved`.
  var orderSeed: UInt64?
  /// Seconds to dwell on a neutral field before each cell, giving every cell the
  /// same starting state instead of the previous cell's settled one.
  var resetInterstitialSeconds: Double?
  /// Put a canonical glass surface on the neutral field during that dwell.
  ///
  /// A bare field resets the *backdrop* but removes the material, so each cell's
  /// surface is created afresh against neutral. This resets to a known *glass*
  /// state instead: one fixed untinted capsule at rest, the same one before every
  /// cell whatever that cell contains. Fixed rather than matched to the cell
  /// ahead, deliberately — a reset that varied with what came next would be as
  /// many reset states as there are cells, which is the condition being removed.
  var resetCarriesGlass: Bool = false
  /// Refuse the run unless the machine has been idle at least this long.
  var minIdleSeconds: Double?
  /// Which activation pose the whole run presents in. `.active` is every bed
  /// before 2026-09-11 and is the default; `.inactive` is the window recede.
  var pose: CapturePose = .active
  /// Capture only these scene ids, out of the ones the matching profiles declare.
  ///
  /// Absent is the run `capture` has always been: every scene of every profile
  /// whose accessibility matches the machine. A narrowed run exists because the
  /// checking bed is 42 ids inside a 164-scene matrix and capturing the other 122
  /// costs three times the session (claims §5.134 §5's `prerequisite`) — and it
  /// comes with `requireFreshFixtureRoot` below, because narrowing publication is
  /// destructive against an existing bundle.
  var onlyScenes: Set<String>?
  /// Present and attest every cell, capture and write nothing.
  ///
  /// The cheap proof that a session will run: it walks the real order, presents
  /// each scene through the real pose, checks the real attestation and refuses on
  /// the same conditions, and costs the layout dwell rather than the settle loop.
  var dryRun: Bool = false
}

@MainActor
func runCapture(method: CaptureMethod, allowColourlessTints: Bool, options: CaptureOptions) {
  let spec = loadSpec()
  let pose = options.pose

  // The idle gate, before anything is rendered. A capture taken while somebody
  // is using the machine is not a measurement of the material, and on 2026-08-31
  // a chain ran through exactly that without anything in the record saying so.
  // The lock gate, before the idle gate, because a locked machine passes the idle
  // gate by definition. Both poses: an active run cannot become key on a locked
  // screen, and an inactive run's attestation would pass for the wrong reason.
  if Environment.screenIsLocked() != false && options.dryRun {
    // A dry run captures nothing, so the gate is protecting nothing — and this is
    // the check a session most wants to rehearse from wherever it happens to be.
    // Said loudly rather than silently skipped, because "the real pass will refuse
    // here" is the single most useful thing a rehearsal can tell you.
    print("""
      WOULD REFUSE: the login session's screen is LOCKED. A real pass stops here. \
      Unlock the console session before the sitting; everything below is the \
      rehearsal continuing because it captures nothing.
      """)
  } else if Environment.screenIsLocked() != false {
    fail("""
      the login session's screen is LOCKED\
      \(Environment.screenIsLocked() == nil ? " (or the session could not be read, which is not the same as unlocked)" : "").

      No application can become active and no window can become key on a locked \
      screen, so an active run would capture the unfocused material under active \
      ids — and an INACTIVE run is worse, because both halves of its attestation \
      are false for the wrong reason and every cell would attest while the window \
      server composites nothing the bed is about. The idle gate cannot catch this: \
      a locked machine is maximally idle.

      Unlock the console session, disable the screen saver and display sleep for \
      the length of the sitting, and re-run. Nothing was captured.
      """)
  }
  let idleAtStart = Environment.hidIdleSeconds()
  let userActive = Environment.userIsActiveAsserted()
  if let bar = options.minIdleSeconds {
    guard let idle = idleAtStart else {
      fail("""
        --min-idle-seconds \(bar) was asked for, but IOHIDSystem did not answer. \
        A run cannot claim an idle machine on a reading it does not have.
        """)
    }
    if idle < bar {
      fail("""
        the machine has been idle \(String(format: "%.1f", idle))s, under the \
        \(String(format: "%.1f", bar))s this run requires\
        \(userActive == true ? ", and a user-activity assertion is held" : ""). \
        Liquid Glass adapts over seconds and a disturbed session captures the \
        adaptation rather than the material. Leave the machine alone and re-run.
        """)
    }
  }
  let scale = captureScale()
  let canvas = spec.canvas.cgSize
  let root = fixturesDir()

  // A narrowed or inactive run may not be published into a bundle that already
  // exists, and the reason is the publish step rather than the capture: `finish`
  // replaces a captured profile's manifest entry and `promote` replaces its whole
  // directory, both wholesale. Against the committed bundle a 42-cell run would
  // therefore DELETE the other 122 cells of every profile it touched, and the
  // merge would re-encode every carried-forward entry through `FixtureEntry`,
  // which has no field for `recoveredProvenance`, `stateFrequencies`,
  // `observedStates` or `frequencySettled` — four fields the committed manifest
  // carries on 121 and 102 entries and this type would silently drop.
  //
  // Neither is a new hazard; what is new is a flag that makes it reachable by
  // accident. So both narrowed forms require a fresh root, which is also how the
  // multi-run protocol already works (each raw run is its own snapshot, and
  // `materialize` decides what is published from them). claims §5.134 §5's stop
  // condition — "a checking-bed cell whose id already exists" — holds here by
  // construction, because in a fresh root no id exists.
  if options.pose == .inactive || options.onlyScenes != nil {
    let existing = "\(root)/manifest.json"
    if FileManager.default.fileExists(atPath: existing) {
      fail("""
        \(options.pose == .inactive ? "--inactive" : "--scenes") refuses to publish \
        into \(root): a manifest.json is already there.

        A narrowed run republishes each profile it captures WHOLESALE — the \
        manifest entry and the directory — so every cell of that profile it did \
        not capture would be deleted, and every recovered-provenance and \
        run-frequency field on the entries it carried forward would be dropped by \
        the merge. A checking-bed cell whose id already exists is a stop.

        Point VITREA_FIXTURES at an empty directory, run './capture.sh backgrounds' \
        into it at this scale first, and materialise from the raw runs afterwards. \
        Nothing was captured and no window was opened.
        """)
    }
  }

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

  // The interstitial's neutral field, built once. Mid-grey rather than black or
  // white: a reset should start the material from a level that is not itself one
  // of the states it is suspected of settling into. It is never written and
  // never captured — the manifest records the dwell instead.
  let neutralField = Backgrounds.render(.solid(srgb: [128, 128, 128]), canvas: canvas, scale: scale)
  /// The canonical surface for `--reset-glass`, resolved once and reused.
  let resetComponent = spec.components["capsule-button"]
  if options.resetCarriesGlass && resetComponent == nil {
    fail("--reset-glass needs a 'capsule-button' component in scenes.json to reset onto; the spec declares none.")
  }
  let resetScene = SceneEntry(id: "__reset__", background: "__neutral__",
                              component: "capsule-button", state: "rest", tint: nil, label: nil)

  var profileManifests: [ProfileManifest] = []
  var caveats: [String] = []

  // One reusable window for the on-screen paths, so window creation cost and any
  // first-window compositing warm-up do not land on the first scene only.
  let window: NSWindow? = (method == .imageRenderer)
    ? nil
    : Capture.makeWindow(canvas: canvas, keyCapable: pose == .active)
  if let w = window, pose == .active { Capture.present(w) }
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
    if options.dryRun {
      // A dry run proves the presentation and the attestation and nothing else,
      // so it publishes nothing — not even the staging directory it never used.
      try? FileManager.default.removeItem(atPath: stagingDirectory ?? "")
      stagingDirectory = nil
      print("dry run complete: every cell presented and attested in the \(pose.rawValue) pose.")
      print("Nothing was captured, nothing was written, and \(root) is untouched.")
      NSApp.terminate(nil)
      return
    }
    // The measured emptiness summary. Stated as a count, because "the material
    // did not render" is a claim a reader should be able to check against a number.
    let all = profileManifests.flatMap(\.fixtures)

    // The material's ACTIVE appearance is the one every fidelity claim means, and
    // it is a condition of the capture rather than a property of the scene — so
    // it is counted here, beside the emptiness summary, rather than assumed.
    let inactive = all.filter { $0.presentedActive == false }
    if pose == .inactive {
      // The same count, read the other way round. On an inactive run every cell
      // is meant to be here, and the fact worth recording is that every one of
      // them proved it — a cell that did not was refused before it was captured,
      // so this number equalling the total is the bed's own attestation summary.
      caveats.append("""
        \(inactive.count) of \(all.count) fixtures were captured in the INACTIVE \
        pose, which is what this run is: the .accessory activation policy, a \
        window that cannot become key, and no activation on any path \
        (Capture.presentInactive). Every entry carries a per-cell \
        `presentation` attestation sampled immediately before its capture, with \
        `isKeyWindow` and `appIsActive` recorded separately — claims §5.134 §5's \
        inversion of `presentedActive`, which is written false here rather than \
        left absent as it is on all 121 recovered fixtures. These cells record \
        the window-recede pose deliberately and are NOT comparable with the \
        active bed's cells of the same scene.
        """)
    } else if !inactive.isEmpty {
      caveats.append("""
        \(inactive.count) of \(all.count) fixtures were captured while the window \
        was NOT key or the app was NOT active. Liquid Glass renders a flat, \
        neutral INACTIVE appearance in that state — it is where the 2026-08-30 \
        bed's author tints went — so these fixtures record the material's \
        unfocused pose regardless of what their profile key says. The harness now \
        makes its borderless window key-capable and activates before presenting \
        (Capture.present); a run that still reports this was denied activation by \
        the session, and needs an interactive login session with nothing stealing \
        focus.
        """)
    }

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
      schemaVersion: 3,
      sceneSpecVersion: spec.version,
      generatedAt: Environment.timestamp(),
      hardware: Environment.hardware(),
      backgrounds: mergedBackgrounds,
      profiles: mergedProfiles,
      split: .init(calibration: spec.split.calibration,
                   validation: spec.split.validation,
                   holdout: spec.split.holdout,
                   recorded: spec.split.recorded ?? [],
                   probe: spec.split.probe ?? [],
                   note: """
                     Holdout scene ids are declared here, as data. Tuning code must \
                     read the 'calibration' list; it must never name a holdout scene. \
                     A 'recorded' scene is captured and committed and read by nothing: \
                     no fit, no self-check, no bound and no claim may cite it. A \
                     'probe' scene is the other way round: fits and claims read it, \
                     and no adopted bound, regression floor or conditioning exclusion \
                     is stated over it, so the frozen bed's gate does not move with it.
                     """),
      caveats: caveats,
      captureProtocol: .init(
        runLabel: options.runLabel,
        orderSeed: options.orderSeed,
        resetInterstitialSeconds: options.resetInterstitialSeconds,
        resetCarriesGlass: options.resetCarriesGlass,
        minIdleSeconds: options.minIdleSeconds,
        hidIdleSecondsAtStart: idleAtStart,
        // Read here rather than at the top: a run that was quiet when it started
        // and busy when it ended is the case worth catching, and only the second
        // reading catches it.
        hidIdleSecondsAtEnd: Environment.hidIdleSeconds(),
        userIsActiveAtStart: userActive))

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
  /// A seed permutes it, and the seed is recorded in the manifest.
  ///
  /// The default — no seed — is still the one fixed order, because that is what
  /// makes two ordinary runs comparable. A seeded run is deliberately *not*
  /// comparable with an unseeded one on order-sensitive grounds, which is the
  /// point: permuting the order is how "does position in the run decide which
  /// cells are unstable" becomes a question the bed can answer instead of a
  /// story about it.
  func interleaved(_ items: [(ProfileSpec, SceneEntry)], seed: UInt64?) -> [(ProfileSpec, SceneEntry)] {
    func fnv1a(_ s: String) -> UInt64 {
      var h: UInt64 = seed ?? 0xcbf2_9ce4_8422_2325
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

  // The scene filter, applied last, so that "which profiles is this machine in a
  // position to capture" and "which cells did this run ask for" stay separate
  // questions and the second is asked against what the first actually left. An id
  // that no selected profile declares is a failure rather than a silent omission:
  // a session that asked for 42 cells and banked 40 would be a bed missing two
  // cells with nothing in it saying which.
  if let wanted = options.onlyScenes {
    let reachable = Set(work.map { $0.1.id })
    let unreachable = wanted.subtracting(reachable).sorted()
    guard unreachable.isEmpty else {
      fail("""
        --scenes names \(unreachable.count) id(s) that no profile selected by this \
        run declares: \(unreachable.joined(separator: ", ")).

        A profile is selected when its a11y mode matches this machine's \
        ('\(systemA11y)') and its key states this display's scale \
        ('\(scaleToken)'). Nothing was captured.
        """)
    }
    work.removeAll { !wanted.contains($0.1.id) }
    caveats.append("""
      Narrowed by --scenes to \(work.count) cells over \
      \(Set(work.map { $0.0.key }).count) profile(s). This bundle is therefore NOT \
      a whole profile: it describes exactly the cells named, which is why it is \
      written into a fresh fixture root — publication is by whole profile \
      directory, so a merge into an existing bundle would delete everything it \
      omits.
      """)
  }

  let order = interleaved(work, seed: options.orderSeed)
  print("capturing \(order.count) fixtures via \(method.rawValue) at \(backingScale)x (interleaved)")

  var byProfile: [String: [FixtureEntry]] = [:]
  /// The colour space the captured images actually carry, per profile. Recorded as
  /// an observation rather than restating the space the capture path requested, so
  /// the manifest field is something a later check can bind against.
  var colorSpaceByProfile: [String: String] = [:]

  /// The scene this one would be if it declared no tint.
  ///
  /// Per contract X2 a tint is not a key axis and not a fourth id segment: it
  /// folds into the THIRD segment as a suffix on the state
  /// (`photo__capsule-button__rest-tint-orange`). Stripping that suffix is
  /// therefore how a tinted cell names its own control, and it is a pure function
  /// of the id — no registry lookup, so it stays correct for a tint id nobody
  /// remembered to register.
  func untintedTwinId(of sceneId: String) -> String? {
    let parts = sceneId.components(separatedBy: "__")
    guard parts.count == 3, let marker = parts[2].range(of: "-tint-") else { return nil }
    return "\(parts[0])__\(parts[1])__\(parts[2][..<marker.lowerBound])"
  }

  /// Close the tint attestation: compare what each tinted capture APPLIED against
  /// what its pixels actually show, and refuse to publish a bed whose tints did
  /// not reach the material.
  ///
  /// Two tests, deliberately unlike each other:
  ///
  ///   IDENTITY   Two scenes that share a backdrop, a component and a state and
  ///              differ only in which tint they declare cannot produce identical
  ///              files if the seed reached the material — `systemOrange` and
  ///              `systemBlue` are not the same colour. No threshold, no colour
  ///              model, nothing to tune. This is the test that condemns.
  ///   RESPONSE   Chroma added over the backdrop, against the same scene captured
  ///              untinted. Weaker (it needs a floor), but it reaches the case
  ///              identity cannot: a bed declaring one seed per scene has no
  ///              identical pair to find, and would otherwise sail through.
  ///
  /// Both run at the end rather than per cell, because the interleaved order puts
  /// a scene and its twin arbitrarily far apart — and because failing here, before
  /// the staged bundle is promoted, leaves the committed fixtures untouched.
  ///
  /// Mutates the captured `byProfile` directly rather than taking it `inout`: the
  /// caller is a sibling nested function over the same local, and passing it as an
  /// inout argument would be an overlapping access to a variable both already
  /// capture.
  func attestTints() {
    var colourless: [String] = []
    var identicalPairs: [String] = []
    // The declared state of a captured cell, read from the spec rather than
    // re-derived from its id: the id's third segment carries the tint and the
    // interaction as suffixes too, so parsing it here would be a second, weaker
    // copy of a rule `SceneEntry` already holds.
    let stateById = Dictionary(uniqueKeysWithValues: spec.scenes.map { ($0.id, $0.state) })
    func mayCondemn(_ sceneId: String) -> Bool {
      TintResolver.attestationMayCondemn(state: stateById[sceneId] ?? "rest")
    }

    // Over a snapshot of the keys, not over the dictionary: the body mutates
    // `byProfile`, and iterating the collection being mutated is a subtlety this
    // does not need. Sorted so a failure report reads the same way twice.
    for profileKey in byProfile.keys.sorted() {
      let entries = byProfile[profileKey] ?? []
      let chromaById = Dictionary(uniqueKeysWithValues: entries.map { ($0.sceneId, $0.chromaShift) })

      // RESPONSE.
      for i in entries.indices where entries[i].tint != nil {
        let id = entries[i].sceneId
        guard let twinId = untintedTwinId(of: id),
              let twinChroma = chromaById[twinId] ?? nil,
              let own = entries[i].chromaShift else { continue }
        let reached = TintResolver.colourReachedMaterial(own: own, untintedTwin: twinChroma)
        byProfile[profileKey]?[i].tint?.untintedTwinChromaShift = twinChroma
        byProfile[profileKey]?[i].tint?.colourReachedMaterial = reached
        // Measured and recorded either way; only the refusal is withheld in the
        // recede, where "the colour did not reach the material" is the finding.
        if !reached && mayCondemn(id) {
          colourless.append(String(
            format: "%@/%@: chroma %.4f vs untinted twin %.4f (+%.4f, floor %.1f)",
            profileKey, id, own, twinChroma, own - twinChroma, TintResolver.chromaResponseFloor))
        }
      }

      // IDENTITY. Grouped by the control they share, so the members of a group
      // differ only in their declared tint.
      var groups: [String: [FixtureEntry]] = [:]
      for e in entries where e.tint != nil {
        guard let twinId = untintedTwinId(of: e.sceneId) else { continue }
        groups[twinId, default: []].append(e)
      }
      for (twinId, members) in groups where members.count > 1 {
        for a in members.indices {
          for b in (a + 1)..<members.count {
            guard members[a].tint?.tintId != members[b].tint?.tintId else { continue }
            // The recede is where two seeds legitimately produce one picture, so
            // a byte-identical pair there is the expected reading rather than a
            // lost tint — the same exemption `gates.ts` makes on the consumer
            // side. Skipped before the file read, because the read is the cost.
            guard mayCondemn(members[a].sceneId), mayCondemn(members[b].sceneId) else { continue }
            // Read back what was actually written, so this compares the published
            // artefact rather than an in-memory value that could differ from it.
            guard let da = try? Data(contentsOf: URL(fileURLWithPath: "\(staging)/\(members[a].file)")),
                  let db = try? Data(contentsOf: URL(fileURLWithPath: "\(staging)/\(members[b].file)")),
                  da == db else { continue }
            identicalPairs.append(
              "\(profileKey): \(members[a].sceneId) and \(members[b].sceneId) are byte-identical " +
              "(same scene '\(twinId)', tints '\(members[a].tint?.tintId ?? "?")' vs " +
              "'\(members[b].tint?.tintId ?? "?")')")
          }
        }
      }
    }

    guard !colourless.isEmpty || !identicalPairs.isEmpty else { return }
    let report = """
      The author tint did not reach the material in this run.

      \(identicalPairs.isEmpty ? "" : "Byte-identical captures declaring different seeds:\n  - "
        + identicalPairs.sorted().joined(separator: "\n  - ") + "\n")
      \(colourless.isEmpty ? "" : "Tinted captures whose chroma response matches their untinted twin:\n  - "
        + colourless.sorted().joined(separator: "\n  - ") + "\n")
      Every tint resolved correctly before the API — './capture.sh tint-doctor' \
      reports the sRGB the Glass value carried — so the colour was lost inside the \
      material, not in this harness. These fixtures record the untinted material \
      under a tinted scene id; no tint number may be fitted on them.
      """
    if allowColourlessTints {
      caveats.append(report + "\n\nPublished anyway: --allow-colourless-tints was passed.")
      print("CAVEAT: the tint did not reach the material; publishing because --allow-colourless-tints was passed")
    } else {
      fail(report + """


        Nothing was published; the committed fixtures and manifest are unchanged. \
        Pass --allow-colourless-tints to publish this bed anyway, with the finding \
        recorded in the manifest's caveats.
        """)
    }
  }

  /// Capture one scene, then recurse to the next — the on-screen paths need the
  /// run loop to turn between scenes for the window server to composite the new
  /// content, which a `for` loop would never let happen.
  func step(_ index: Int) {
    guard index < order.count else {
      attestTints()
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

    // `validate()` has already refused any scene naming a tint the registry does
    // not hold, so a nil here means the scene declared none.
    let tintSpec = scene.tint.flatMap { id in spec.tints?[id].map { (id, $0) } }
    let tint = tintSpec?.1.color
    let attestation = tintSpec.map { TintResolver.attest(id: $0.0, spec: $0.1) }

    // The pre-render half of the tint attestation, checked before a pixel exists
    // because it is answerable there: if the declared hue is already gone from the
    // resolved `Color` or from the `Glass` value built out of it, the fault is in
    // this harness and capturing would only photograph it.
    if let a = attestation, !a.colourSurvivedResolution || !a.glassValueDistinguishesHue {
      fail("""
        scene '\(scene.id)': the tint '\(a.tintId)' lost its colour BEFORE the \
        material. Declared sRGB\(a.declaredSRGB) a=\(a.declaredAlpha); \
        Color.resolve(in:) gave \(a.resolvedSRGB) a=\(a.resolvedOpacity) \
        (chroma \(a.resolvedChroma)); the Glass value \
        \(a.glassValueDistinguishesHue ? "does" : "does NOT") tell that hue apart \
        from another at the same alpha. This is a harness fault, not an OS one — \
        run './capture.sh tint-doctor' for the per-tint breakdown.
        """)
    }

    let view = SceneView(scene: scene, component: component, backgroundImage: bg,
                         canvas: canvas, pressed: scene.state == "pressed", tint: tint)
      .profileEnvironment(colorScheme: profile.colorScheme, a11y: profile.a11y)

    let dir = "\(staging)/\(profile.key)"
    let file = "\(scene.id).png"

    /// The pose gate for this cell, sampled immediately before its capture.
    ///
    /// Only the inactive pose is gated, and the asymmetry is deliberate. On the
    /// active path a cell that lost activation has always been RECORDED —
    /// `presentedActive: false` plus a run caveat — and that behaviour is left
    /// exactly as it is, because the whole active bed's provenance is compared
    /// against it. On the inactive path the same laxity is what claims §5.134 §5
    /// names as the thing that must stop: an inactive id may not be written
    /// unless the pose was proved for that cell, so this refuses the run instead
    /// of publishing the cell with a note.
    func attestPose(_ w: NSWindow) -> PresentationAttestation? {
      guard pose == .inactive else { return nil }
      guard Capture.isInactivelyPresented(w) else {
        fail("""
          scene '\(scene.id)': the inactive pose was lost before this cell. The \
          window is \(w.isKeyWindow ? "KEY" : "not key") and the application is \
          \(NSApp.isActive ? "ACTIVE" : "not active"); both must be false.

          Something activated this process mid-run — a click into the window, an \
          AppleScript or launcher activation, an assistive tool. The capture \
          stops here rather than file an active cell under an inactive id, which \
          is the one failure mode the recovered bed cannot rule out about itself. \
          Nothing was published; the fixtures and manifest under \(root) are \
          unchanged. Re-run the pass; leave the machine alone while it runs.
          """)
      }
      return PresentationAttestation(
        declaredPose: pose.rawValue,
        observedPose: CapturePose.inactive.rawValue,
        isKeyWindow: w.isKeyWindow,
        appIsActive: NSApp.isActive,
        activationPolicy: NSApp.activationPolicy() == .accessory ? "accessory" : "regular",
        windowCanBecomeKey: w.canBecomeKey,
        mechanism: "accessory-policy+non-key-window+orderFrontRegardless",
        attestedAt: Environment.timestamp())
    }

    func record(_ image: CGImage, _ deterministic: Bool?, _ noise: Double?,
                presentation: PresentationAttestation? = nil,
                settleIterations: Int? = nil, settleSeconds: Double? = nil) {
      do { try Backgrounds.writePNG(image, to: "\(dir)/\(file)") }
      catch { fail("writing \(file): \(error.localizedDescription)") }

      colorSpaceByProfile[profile.key] = (image.colorSpace?.name).map { $0 as String } ?? "sRGB"

      // The pose, re-read HERE, at the moment `presentedActive` is sampled.
      //
      // `attestPose` runs before the dwell, because the pose has to have held for
      // the frames that produced these bytes; but the settle loop is up to ten
      // seconds long, and a pose lost inside that window would be written as
      // `presentedActive: true` beside an attestation saying `inactive`, and
      // refused only at the NEXT cell — after this one was already filed. The two
      // readings bracket the capture, and a cell is written only if both hold.
      if pose == .inactive, let w = window, !Capture.isInactivelyPresented(w) {
        fail("""
          scene '\(scene.id)': the inactive pose held when this cell was attested \
          and was LOST before its bytes were recorded — the window is \
          \(w.isKeyWindow ? "KEY" : "not key") and the application is \
          \(NSApp.isActive ? "ACTIVE" : "not active") now.

          The settle loop is seconds long and something activated this process \
          inside it, so this cell's pixels are not all of one pose. Nothing was \
          published; the fixtures and manifest under \(root) are unchanged. \
          Re-run the pass and leave the machine alone while it runs.
          """)
      }

      // Measure how much the component actually contributed, rather than assuming
      // it contributed anything.
      let vsBackground = try? Capture.compare(image, bg)
      let chroma = (try? Capture.chromaShift(image, background: bg)) ?? nil
      byProfile[profile.key, default: []].append(FixtureEntry(
        sceneId: scene.id, file: "\(profile.key)/\(file)", fixtureSet: set,
        orderIndex: index,
        hidIdleSeconds: Environment.hidIdleSeconds(),
        settleIterations: settleIterations, settleSeconds: settleSeconds,
        captureMethod: method.rawValue, materialRendered: method.materialRendered,
        width: image.width, height: image.height,
        deterministic: deterministic, repeatNoise: noise,
        identicalToBackground: vsBackground.map { $0.maxDelta == 0 },
        deltaFromBackground: vsBackground?.mad,
        chromaShift: chroma.map { (($0 * 10000).rounded()) / 10000 },
        presentedActive: window.map { Capture.isActivelyPresented($0) },
        presentation: presentation,
        tint: attestation,
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

      // The reset interstitial, when asked for: a neutral field held long enough
      // for the material to settle on it, so this cell begins from a state the
      // protocol chose rather than from whatever the previous cell left behind.
      // It is a step in the protocol and never a fixture — nothing is captured
      // or recorded here, and the manifest names the dwell instead.
      func beginScene() {
        w.contentView = NSHostingView(rootView: view)
        w.displayIfNeeded()
        // Two turns of the run loop plus a short settle: the first lets AppKit lay
        // out the new content, the wait lets the window server composite it. Without
        // it the first capture of each scene is the previous scene's material.
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.25) { afterLayout() }
      }
      func afterLayout() {
        if options.dryRun {
          // The whole run, minus the two expensive halves: no settle loop and no
          // capture. What it does exercise is everything that can refuse — the
          // fixture root, the backgrounds, the scene resolution, the tint
          // pre-check, the presentation and this cell's pose attestation.
          let attested = attestPose(w)
          let mark = attested.map { " \($0.observedPose) key=\($0.isKeyWindow) active=\($0.appIsActive)" }
            ?? (Capture.isActivelyPresented(w) ? " active" : " NOT-ACTIVE")
          print("  [\(index + 1)/\(order.count)] \(profile.key)/\(scene.id) dry-run\(mark)")
          step(index + 1)
          return
        }
        if method == .cacheDisplay {
          let attested = attestPose(w)
          guard let a = try? Capture.cacheDisplay(w), let b = try? Capture.cacheDisplay(w) else {
            fail("cacheDisplay failed for \(scene.id)")
          }
          let cmp = try? Capture.compare(a, b)
          record(a, cmp.map { $0.maxDelta == 0 }, cmp?.mad, presentation: attested)
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
              //
              // The iteration count and elapsed dwell are recorded from
              // 2026-08-31: this loop asks whether the image STOPPED MOVING, which
              // is not the same as whether it converged to the same place. A cell
              // that agrees on the first comparison and one that agrees on the
              // sixth are different evidence, and both previously recorded the
              // identical `deterministic: true`.
              // Attested before the dwell, not after the loop: the pose has to
              // have held for the frames that produced these bytes, and a reading
              // taken nine seconds later would describe a different moment.
              let attested = attestPose(w)
              let began = Date()
              try await Task.sleep(nanoseconds: 1_750_000_000)
              var previous = try await Capture.screenCaptureKit(windowID: CGWindowID(w.windowNumber), pixelSize: px)
              var settled = false
              var lastMad = 0.0
              var iterations = 0
              for _ in 0..<7 {
                try await Task.sleep(nanoseconds: 1_000_000_000)
                iterations += 1
                let next = try await Capture.screenCaptureKit(windowID: CGWindowID(w.windowNumber), pixelSize: px)
                let cmp = try Capture.compare(previous, next)
                lastMad = cmp.mad
                previous = next
                if cmp.maxDelta == 0 { settled = true; break }
              }
              record(previous, settled, settled ? 0 : lastMad,
                     presentation: attested,
                     settleIterations: iterations,
                     settleSeconds: Date().timeIntervalSince(began))
            } catch {
              fail(error.localizedDescription)
            }
            step(index + 1)
          }
        }
      }

      guard let dwell = options.resetInterstitialSeconds else { return beginScene() }
      if options.resetCarriesGlass, let resetComponent {
        w.contentView = NSHostingView(rootView:
          SceneView(scene: resetScene, component: resetComponent, backgroundImage: neutralField,
                    canvas: canvas, pressed: false, tint: nil)
            .profileEnvironment(colorScheme: profile.colorScheme, a11y: profile.a11y))
      } else {
        w.contentView = NSHostingView(rootView: RasterBackground(image: neutralField, canvas: canvas)
          .frame(width: canvas.width, height: canvas.height))
      }
      w.displayIfNeeded()
      DispatchQueue.main.asyncAfter(deadline: .now() + dwell) { beginScene() }
    }
  }

  switch pose {
  case .active:
    step(0)
  case .inactive:
    // The pose is reached before the first cell and refused here if it is not,
    // with no window content, nothing staged and nothing written. It has to be
    // awaited rather than asserted: AppKit updates the application's active state
    // from its own event loop, so the answer exists only after this function has
    // given the loop back.
    Task { @MainActor in
      guard let w = window else { fail("the inactive pose needs a window") }
      do { try await Capture.presentInactive(w) }
      catch { fail(error.localizedDescription) }
      print("presenting INACTIVE: key=\(w.isKeyWindow) NSApp.isActive=\(NSApp.isActive) " +
            "policy=\(NSApp.activationPolicy() == .accessory ? "accessory" : "regular") " +
            "canBecomeKey=\(w.canBecomeKey)")
      step(0)
    }
  }
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

    case "deactivate-probe":
      // `--launch` picks which half is measured; see runDeactivateProbe.
      // Measures the candidate deactivation mechanisms and reports what this
      // machine does with each. A window, no TCC-free promise (it asks
      // ScreenCaptureKit whether an inactive window is still capturable) and no
      // fixture directory: it writes nothing anywhere.
      //
      // `.accessory` BEFORE `app.run()`, exactly as `capture --inactive` sets it.
      // The adopted mechanism is "the policy was never `.regular`", so a probe
      // that launched `.regular` and flipped afterwards would be measuring the
      // recovery case (arm E) and reporting it as the adopted one.
      let launch = value(of: "--launch", in: args) ?? "accessory"
      guard launch == "accessory" || launch == "regular" else {
        fail("--launch takes 'accessory' or 'regular', not '\(launch)'")
      }
      runGUI(policy: launch == "accessory" ? .accessory : .regular) { runDeactivateProbe() }

    case "rehearse-tints":
      // No window, no TCC, no capture: it reads a bundle that already exists and
      // says whether a run that produced it would have been refused.
      let rehearsalPose = value(of: "--pose", in: args) ?? "active"
      guard let p = CapturePose(rawValue: rehearsalPose) else {
        fail("--pose takes 'active' or 'inactive', not '\(rehearsalPose)'")
      }
      runRehearseTints(pose: p)

    case "manifest-doctor":
      // Reads the committed manifest and writes nothing. No window, no TCC.
      runManifestDoctor()

    case "tint-doctor":
      // No window and no TCC grant: every question it answers is about values —
      // the Color a registry entry builds, what SwiftUI resolves it to, and
      // whether the resulting Glass still tells two hues apart.
      runTintDoctor()

    case "dump-layers":
      // Reads Apple's own material parameters out of the layer tree. It needs a
      // presented, key window — hence runGUI — but no TCC grant and no fixture
      // directory, because it captures nothing.
      let ids = value(of: "--scenes", in: args)
        .map { $0.split(separator: ",").map(String.init).filter { !$0.isEmpty } }
        ?? DUMP_LAYER_DEFAULT_SCENES
      let out = value(of: "--out", in: args) ?? "\(ROOT)/build/layer-dumps"
      var settle = 1.5
      if let raw = value(of: "--settle", in: args) {
        guard let parsed = Double(raw), parsed >= 0 else {
          fail("--settle takes a non-negative number of seconds, not '\(raw)'")
        }
        settle = parsed
      }
      refuseScenesUnreachableInPose(ids, in: loadSpec(), pose: .active, remediation: """
        Pass --scenes naming only scenes this harness can reproduce (the \
        default twelve-scene set is all 'rest' or 'pressed'), or point \
        VITREA_SCENES at a spec with none of these.
        """)
      let scheme = value(of: "--scheme", in: args)
      runGUI { runDumpLayers(sceneIds: ids, outDir: out, settleSeconds: settle, scheme: scheme) }

    case "capture":
      let raw = value(of: "--method", in: args) ?? "screencapturekit"
      guard let method = CaptureMethod(rawValue: raw) else {
        fail("unknown --method '\(raw)'. One of: " +
             "swiftui-image-renderer, nsview-cachedisplay, screencapturekit")
      }
      // The producer-side twin of `compare.ts --allow-colourless-tints`. Without
      // it a bed whose tints did not reach the material is refused rather than
      // published; with it, the run publishes and says so in the manifest. Same
      // posture as `--method`: the harness does not decide this quietly.
      let allow = args.contains("--allow-colourless-tints")

      // The study knobs. Every one of them defaults to the capture every
      // committed bed was taken under, so a run that names none of them is the
      // run it always was — and any run that names one records it in the
      // manifest, because a protocol nobody wrote down is how two beds come to
      // disagree with no way to ask why.
      func number(_ flag: String) -> Double? {
        guard let raw = value(of: flag, in: args) else { return nil }
        guard let parsed = Double(raw), parsed >= 0 else {
          fail("\(flag) takes a non-negative number of seconds, not '\(raw)'")
        }
        return parsed
      }
      var options = CaptureOptions()
      options.runLabel = value(of: "--run-label", in: args)
      if let raw = value(of: "--order-seed", in: args) {
        guard let seed = UInt64(raw) else { fail("--order-seed takes an unsigned integer, not '\(raw)'") }
        options.orderSeed = seed
      }
      options.resetInterstitialSeconds = number("--reset-interstitial")
      options.resetCarriesGlass = args.contains("--reset-glass")
      if options.resetCarriesGlass && options.resetInterstitialSeconds == nil {
        fail("--reset-glass needs --reset-interstitial <s>: a reset with no dwell is not a reset.")
      }
      options.minIdleSeconds = number("--min-idle-seconds")
      options.pose = args.contains("--inactive") ? .inactive : .active
      options.dryRun = args.contains("--dry-run")
      if let raw = value(of: "--scenes", in: args) {
        let ids = raw.split(separator: ",").map(String.init).filter { !$0.isEmpty }
        guard !ids.isEmpty else { fail("--scenes was given an empty list.") }
        options.onlyScenes = Set(ids)
      }
      if options.pose == .inactive && method == .imageRenderer {
        fail("""
          --inactive has no meaning for --method swiftui-image-renderer: that path \
          renders offscreen and has no window to be inactive. It does not render \
          the material either. Use screencapturekit.
          """)
      }

      // The preflight, before a window exists. `NSWorkspace`'s accessibility
      // properties need no GUI, so the set of cells this invocation would attempt
      // is knowable here and a refusal costs nothing to undo.
      let captureSpec = loadSpec()
      let systemA11yPreflight = SystemAccessibility.current
      var candidateIds = Set(captureSpec.profiles
        .filter { $0.a11y == systemA11yPreflight }
        .flatMap { captureSpec.scenes(for: $0).map(\.id) })
      if let wanted = options.onlyScenes { candidateIds.formIntersection(wanted) }
      // The no-text rule, enforced before anything else and in either pose. A
      // labelled scene is not capturable in the way an inactive scene is
      // capturable in the other pose — it is not capturable at all, because the
      // fixture bed's whole claim to measure the material rests on there being no
      // glyph rasteriser inside the region being measured (SceneViews.swift
      // rule 2). Only `dump-layers` renders one, and it captures no pixels.
      let labelled = captureSpec.scenesDeclaringALabel(candidateIds)
      if !labelled.isEmpty {
        fail("""
          \(labelled.count) of the requested scenes declare a label: \
          \(labelled.joined(separator: ", ")).

          No capture path renders text inside the glass, in either pose, at any \
          scale. A label would put a glyph rasteriser inside the region the \
          fixture exists to measure, which is the rule the whole bed's \
          trustworthiness rests on. Labelled scenes are for './capture.sh \
          dump-layers', which reads Apple's configuration and captures no pixels \
          (claims §5.133 §7).

          Nothing was captured and no window was opened.
          """)
      }
      refuseScenesUnreachableInPose(candidateIds, in: captureSpec, pose: options.pose,
                                    remediation: options.pose == .inactive ? """
        Pass --scenes naming only 'inactive' ids — the checking bed's list is in \
        packages/calibration/results/2026-09-11-w27c-g1b/checking-bed.json and the \
        runbook quotes it — or point VITREA_SCENES at a spec of inactive scenes.
        """ : """
        Pass --scenes naming only 'rest' and 'pressed' ids, run the recede with \
        --inactive instead, or point VITREA_SCENES at a spec with no inactive \
        scenes for this a11y mode.
        """)

      // The activation policy is a launch-time property of the process and half of
      // the inactive mechanism, so it is decided here, before AppKit starts, and
      // never toggled mid-run. `VITREA_ACTIVATION_POLICY` cannot override an
      // inactive run into `.regular`: that would be an env var quietly turning the
      // pose into the one it is not.
      runGUI(policy: options.pose == .inactive ? .accessory : nil) {
        runCapture(method: method, allowColourlessTints: allow, options: options)
      }

    default:
      fail("""
        usage: harness [backgrounds|probe|deactivate-probe|manifest-doctor|rehearse-tints|tint-doctor|dump-layers|capture [options]]

        rehearse-tints options:
          --pose <active|inactive>    which pose's tint-attestation rule to apply (default active)

        deactivate-probe options:
          --launch <accessory|regular>  which launch policy's arms to measure (default accessory)

        dump-layers options:
          --scenes <id,id,...>        which scenes to dump; default is the ten-scene set
          --out <dir>                 where the per-scene JSON goes (default build/layer-dumps)
          --settle <s>                seconds to wait after presenting each scene (default 1.5)
          --scheme <light|dark>       the colour scheme to present under (default light)

        capture options:
          --method <m>                swiftui-image-renderer | nsview-cachedisplay | screencapturekit
          --inactive                  present the window in the WINDOW-RECEDE pose and attest it
                                      per cell; captures 'inactive' scenes only, needs a fresh
                                      VITREA_FIXTURES root (claims §5.134 §5)
          --scenes <id,id,...>        capture only these ids; needs a fresh VITREA_FIXTURES root
          --dry-run                   present and attest every cell, capture and write nothing
          --allow-colourless-tints    publish a bed whose tints did not reach the material
          --run-label <s>             recorded in the manifest, so a study's arms are separable
          --order-seed <n>            permute the capture order; absent keeps the one stable order
          --reset-interstitial <s>    dwell on a neutral field before each cell
          --reset-glass               that dwell carries a canonical glass surface
          --min-idle-seconds <s>      refuse the run unless the machine has been idle this long
        """)
    }
  }

  private static func value(of flag: String, in args: [String]) -> String? {
    guard let i = args.firstIndex(of: flag), i + 1 < args.count else { return nil }
    return args[i + 1]
  }

  /// `policy` overrides both the default and `VITREA_ACTIVATION_POLICY`, and only
  /// the inactive capture path passes one: the activation policy is half of that
  /// pose's mechanism, so it cannot be left to an environment variable that a
  /// shell profile might be carrying.
  @MainActor
  private static func runGUI(policy: NSApplication.ActivationPolicy? = nil,
                             _ action: @MainActor @escaping () -> Void) {
    let app = NSApplication.shared
    let driver = Driver(action: action)
    app.delegate = driver
    if let policy {
      app.setActivationPolicy(policy)
      withExtendedLifetime(driver) { app.run() }
      return
    }
    // .regular, not .accessory. The harness used to take .accessory so it would
    // not claim the Dock or the menu bar while capturing — polite, and wrong:
    // an .accessory app does not become active, a window of an inactive app
    // cannot become key, and Liquid Glass renders its flat inactive appearance
    // for a window that is not key. The whole committed bed was captured that
    // way. Claiming the Dock for the length of a capture run is the cheaper
    // cost by a wide margin; `VITREA_ACTIVATION_POLICY=accessory` restores the
    // old behaviour for anyone who needs the harness to stay out of the way and
    // is not capturing material.
    let policy = ProcessInfo.processInfo.environment["VITREA_ACTIVATION_POLICY"]
    app.setActivationPolicy(policy == "accessory" ? .accessory : .regular)
    withExtendedLifetime(driver) { app.run() }
  }
}
