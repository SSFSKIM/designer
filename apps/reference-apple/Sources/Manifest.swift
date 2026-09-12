import Foundation
import IOKit
import IOKit.pwr_mgt
import CoreGraphics

/// The fixture manifest — X9's native side, written next to the PNGs.
///
/// Everything in here exists so that a number measured against these fixtures can
/// name the conditions it was measured under. The fields that look like paranoia
/// (`materialRendered`, `requestedScale` vs `actualScale`, `caveats`) are the ones
/// that matter most: this machine cannot currently produce a canonical capture,
/// and a manifest that hid that would turn a known limitation into a silent lie.

struct HardwareInfo: Codable {
  let model: String
  let cpu: String
  let osVersion: String
  let osBuild: String
  let xcodeVersion: String
  let sdk: String
}

struct DisplayInfo: Codable {
  let requestedScale: Double
  /// The window's real `backingScaleFactor`. When it disagrees with
  /// `requestedScale`, the fixture is not the resolution its profile key claims —
  /// see `FixtureManifest.caveats`.
  let actualBackingScale: Double
  let pixelSize: [Int]
  let colorSpace: String
  /// The display the capture window was on, and its colour profile. Captured
  /// bytes depend on the display's colour context — measured 2026-08-29:
  /// photo-backed cells shifted up to 4/255 across an EDID renegotiation of the
  /// same physical panel — so the identity is evidence a reproduction attempt
  /// can bind against, not decoration. Optional: manifests from before the
  /// field carry no claim.
  let displayName: String?
  let displayColorProfile: String?
}

/// The inactive pose's per-cell attestation — the inversion claims §5.134 §5 asks
/// for, written as evidence rather than as an absence.
///
/// Every field is sampled at the moment the pose is checked, immediately before the
/// capture of the cell it is attached to, and the cell is refused if the pose is not
/// the one the run declared. The three state readings are recorded separately rather
/// than reduced to one Boolean because they fail separately: a window that is not key
/// in an application that IS active is a different fault from a `.regular` process
/// that was never deactivated, and a bed that recorded only their conjunction could
/// not say which happened.
struct PresentationAttestation: Codable {
  /// The pose this run declared, and the pose observed. They are equal in every
  /// written entry — a mismatch fails the cell before it is captured — and both are
  /// recorded so that equality is a fact in the file rather than a property of code
  /// nobody can see from the bundle.
  let declaredPose: String
  let observedPose: String
  let isKeyWindow: Bool
  let appIsActive: Bool
  /// `regular` or `accessory`, read from `NSApp.activationPolicy()`. The policy is
  /// half the mechanism, so a bundle that cannot state it cannot say how its pose
  /// was produced.
  let activationPolicy: String
  /// Whether AppKit was allowed to promote the window to key — `canBecomeKey`.
  let windowCanBecomeKey: Bool
  /// A short, stable name for how the pose was reached, so two beds produced by
  /// different mechanisms are never silently pooled.
  let mechanism: String
  /// When the three state readings above were taken. Distinct from `capturedAt`:
  /// the pose is checked before the settle loop starts and the capture ends after
  /// it, and a pose that changed in between is what the two timestamps expose.
  let attestedAt: String
}

struct FixtureEntry: Codable {
  let sceneId: String
  let file: String
  let fixtureSet: String        // calibration | validation | holdout | recorded
  /// Position in this run's capture order, 0-based.
  ///
  /// Recorded because the order is a *condition of the capture*, not a detail of
  /// it: the material's tone adaptation is an animation over seconds, so where a
  /// cell sits in the run is part of what produced its bytes. Without this, a
  /// run captured under a permuted order cannot be compared with one that was
  /// not, and the 2026-08-31 finding that the first cells captured are
  /// over-represented among the unstable ones could not have been checked at all.
  let orderIndex: Int?
  /// Seconds since the last user input, at the moment this cell was captured.
  ///
  /// Per cell rather than per run, so a run disturbed halfway through says which
  /// half. The run-level minimum falls out of these.
  let hidIdleSeconds: Double?
  /// How many settle comparisons this cell needed, and how long it dwelled.
  ///
  /// `deterministic` says two captures a second apart agreed; these say how hard
  /// that was to reach. A cell that agrees on the first comparison and one that
  /// takes six are not the same evidence, and the difference was invisible
  /// before.
  let settleIterations: Int?
  let settleSeconds: Double?
  let captureMethod: String
  let materialRendered: Bool
  let width: Int
  let height: Int
  /// Byte-identical on an immediate repeat capture?
  let deterministic: Bool?
  /// Mean absolute RGB difference between the two repeat captures, 0..255.
  let repeatNoise: Double?
  /// Is this capture pixel-identical to its own background raster?
  ///
  /// The emptiness check, and the reason it is a field rather than a sentence in
  /// `caveats`: when `true`, the component contributed *nothing* to the image, so
  /// the fixture carries no information about the material at all. Anything
  /// reading these fixtures can therefore refuse them mechanically, instead of
  /// relying on a human to have read a note.
  let identicalToBackground: Bool?
  /// Mean absolute RGB difference from the background raster, 0..255. A positive
  /// number is the amount of signal the component actually contributed.
  let deltaFromBackground: Double?
  /// How much CHROMA the component added over its own backdrop, 0..255, across
  /// the pixels it changed — see `Capture.chromaShift`.
  ///
  /// Recorded for every fixture, not only tinted ones, because the untinted cells
  /// are the control: an untinted Liquid Glass body desaturates slightly (this
  /// bed's untinted cells read −3.9…0.0), so "did a tint add colour" is only
  /// answerable against that baseline. Optional: manifests from before the field
  /// carry no claim.
  let chromaShift: Double?
  /// Was the capture window KEY, in an ACTIVE app, at the moment this was taken?
  ///
  /// Liquid Glass has an active and an inactive appearance and the window server
  /// picks between them from this state; the inactive one is flat and neutral. A
  /// fixture captured `false` here is a capture of the material's unfocused pose,
  /// whatever its profile key says. The whole bed committed on 2026-08-30 was
  /// taken through a borderless window that could not become key at all — see
  /// `Capture.CaptureWindow`. Optional: manifests from before the field carry no
  /// claim, and `nil` also covers the offscreen `swiftui-image-renderer` path,
  /// which has no window to be key.
  let presentedActive: Bool?
  /// The pose this cell was captured in, proved rather than absent.
  ///
  /// `presentedActive` alone cannot carry an inactive bed. On the 121 recovered
  /// fixtures the field is simply MISSING, and a missing field is indistinguishable
  /// from a bundle written before the field existed — which is exactly what claims
  /// §5.134 §5 says must stop being acceptable: "the field merely being absent is
  /// what the recovered entries do". So an inactive capture records the two halves
  /// of the attestation separately, beside the mechanism that produced them and the
  /// moment they were read, and `presentedActive` is written `false` as the
  /// inversion it is rather than left out.
  ///
  /// Absent on the active path, where `presentedActive: true` already says
  /// everything and where adding a field would change bytes the existing bed's
  /// provenance is compared against.
  let presentation: PresentationAttestation?
  /// What this capture handed to `Glass.tint(_:)`, and whether any of it came out
  /// the other side. nil on every scene that declares no tint.
  ///
  /// The tint counterpart of `identicalToBackground`: a fact promoted out of prose
  /// and into a typed field so it can be refused mechanically. The 2026-08-30 bed
  /// recorded 18 tinted fixtures as `materialRendered: true, deterministic: true`
  /// while the material was neutral glass, and nothing in the bundle said so — it
  /// took a downstream fit to notice. A capture that records the colour it applied
  /// beside the colour it observed cannot repeat that.
  var tint: TintAttestation?
  let capturedAt: String
}

struct ProfileManifest: Codable {
  let profileKey: String
  let colorScheme: String
  let a11yMode: String
  let display: DisplayInfo
  let fixtures: [FixtureEntry]
  /// Facts about THESE fixtures that must travel with them across runs — e.g.
  /// the macOS toggle-coupling under which the increased-contrast profile was
  /// captured. Run-level `FixtureManifest.caveats` describe only the run that
  /// wrote the file and are replaced wholesale each run; anything profile-scoped
  /// belongs here, where the multi-run merge preserves it. Optional so
  /// schema-1 manifests still decode.
  let caveats: [String]?
}

struct FixtureManifest: Codable {
  /// 3 since 2026-08-31: every fixture now records its position in the capture
  /// order, the machine's idle time when it was taken and how long it took to
  /// settle, and the run records the protocol it was captured under. The bump is
  /// not a field list — it marks the first manifests that can be asked *how* a
  /// bed was produced, which every bed before this one cannot answer.
  let schemaVersion: Int
  let sceneSpecVersion: Int
  let generatedAt: String
  let hardware: HardwareInfo
  let backgrounds: [String: String]
  let profiles: [ProfileManifest]
  let split: SplitDeclaration
  /// Known, deliberate deviations from the spec's canonical conditions in THE
  /// RUN THAT WROTE THIS FILE (skip notes, emptiness counts). Replaced wholesale
  /// each run — profile-scoped facts live on `ProfileManifest.caveats`, which
  /// the multi-run merge preserves. Empty is a claim; a populated list is the
  /// reason a claim must be qualified.
  let caveats: [String]
  /// How this run was produced. Optional so schema-2 manifests still decode.
  let captureProtocol: CaptureProtocol?

  /// The protocol this run was captured under.
  ///
  /// A bed is only comparable with another bed when both were produced the same
  /// way, and until 2026-08-31 nothing in the record said how. This block is what
  /// makes a stability study possible: two runs that disagree can be asked
  /// whether they were run differently before they are asked what the material
  /// did.
  struct CaptureProtocol: Codable {
    /// Free-text label for the run, so a study's arms are separable by name.
    let runLabel: String?
    /// Permutation seed for the capture order. Absent is the fixed, stable order
    /// every bed before this was captured under.
    let orderSeed: UInt64?
    /// Neutral-field dwell inserted before each cell, in seconds. Absent means
    /// no interstitial: each cell begins from whatever the previous one left.
    let resetInterstitialSeconds: Double?
    /// Whether that dwell carried a canonical glass surface rather than a bare field.
    let resetCarriesGlass: Bool?
    /// The idle bar this run was required to clear, and what it actually saw.
    let minIdleSeconds: Double?
    let hidIdleSecondsAtStart: Double?
    let hidIdleSecondsAtEnd: Double?
    /// Whether the power manager reported a user-activity assertion held at the
    /// start of the run. `nil` means the query failed, which is not the same as
    /// `false` and is recorded as itself.
    let userIsActiveAtStart: Bool?
  }

  struct SplitDeclaration: Codable {
    let calibration: [String]
    let validation: [String]
    let holdout: [String]
    /// Captured and committed, read by nothing. See `SplitSpec.recorded`.
    let recorded: [String]
    /// Captured routinely, read by fits and claims, gated by nothing. See
    /// `SplitSpec.probe`. Optional so a manifest written before W25 — every
    /// committed one — still decodes when a later run merges over it.
    let probe: [String]?
    let note: String
  }
}

enum Environment {
  /// Seconds since the last user input event, read from IOHIDSystem's own
  /// counter.
  ///
  /// The direct measure of the thing that matters: not "is the screen unlocked"
  /// but "is anybody touching this machine". On 2026-08-31 a capture chain ran
  /// against a session that was unlocked, on console, and being used, and the
  /// two facts were indistinguishable from the manifest. `nil` means the query
  /// failed, which is not the same as "idle" and must never be read as one.
  static func hidIdleSeconds() -> Double? {
    let service = IOServiceGetMatchingService(kIOMainPortDefault, IOServiceMatching("IOHIDSystem"))
    guard service != 0 else { return nil }
    defer { IOObjectRelease(service) }
    var properties: Unmanaged<CFMutableDictionary>?
    guard IORegistryEntryCreateCFProperties(service, &properties, kCFAllocatorDefault, 0) == KERN_SUCCESS,
          let dict = properties?.takeRetainedValue() as? [String: Any],
          let idle = dict["HIDIdleTime"] as? NSNumber
    else { return nil }
    return idle.doubleValue / 1_000_000_000
  }

  /// Whether the power manager reports a user-activity assertion held right now.
  ///
  /// A second, independent witness to the same question, because the two can
  /// disagree: an assertion can be held by a process while the HID counter
  /// climbs. Recording both means a disturbed run can be told apart from a quiet
  /// one after the fact rather than argued about.
  static func userIsActiveAsserted() -> Bool? {
    var assertions: Unmanaged<CFDictionary>?
    guard IOPMCopyAssertionsStatus(&assertions) == kIOReturnSuccess,
          let dict = assertions?.takeRetainedValue() as? [String: Any]
    else { return nil }
    guard let level = dict["UserIsActive"] as? NSNumber else { return false }
    return level.intValue > 0
  }

  /// Whether the login session's screen is LOCKED right now.
  ///
  /// Measured 2026-09-12, and the reason it is a gate rather than a note: on a
  /// locked screen no application can become active and no window can become key,
  /// so `Capture.present` silently fails to reach the active pose — and the
  /// INACTIVE pose's attestation passes, because both of its halves are false for
  /// the wrong reason. A locked-screen inactive run would therefore attest every
  /// cell while the window server is not compositing the material the bed exists
  /// to photograph. The idle gate does not catch it: a locked machine is maximally
  /// idle.
  ///
  /// `nil` means the query failed, which is not the same as "unlocked" and must
  /// never be read as one.
  static func screenIsLocked() -> Bool? {
    guard let session = CGSessionCopyCurrentDictionary() as? [String: Any] else { return nil }
    guard let locked = session["CGSSessionScreenIsLocked"] as? NSNumber else { return false }
    return locked.boolValue
  }

  static func hardware() -> HardwareInfo {
    HardwareInfo(
      model: sysctl("hw.model"),
      cpu: sysctl("machdep.cpu.brand_string"),
      osVersion: ProcessInfo.processInfo.operatingSystemVersionString,
      osBuild: sysctlOrEmpty("kern.osversion"),
      xcodeVersion: ProcessInfo.processInfo.environment["VITREA_XCODE_VERSION"] ?? "unknown",
      sdk: ProcessInfo.processInfo.environment["VITREA_SDK"] ?? "unknown")
  }

  private static func sysctl(_ name: String) -> String {
    sysctlOrEmpty(name).isEmpty ? "unknown" : sysctlOrEmpty(name)
  }

  private static func sysctlOrEmpty(_ name: String) -> String {
    var size = 0
    guard sysctlbyname(name, nil, &size, nil, 0) == 0, size > 0 else { return "" }
    var buf = [CChar](repeating: 0, count: size)
    guard sysctlbyname(name, &buf, &size, nil, 0) == 0 else { return "" }
    return String(cString: buf)
  }

  static func timestamp() -> String {
    let f = ISO8601DateFormatter()
    f.formatOptions = [.withInternetDateTime]
    return f.string(from: Date())
  }
}
