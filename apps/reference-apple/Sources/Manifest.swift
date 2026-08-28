import Foundation
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

struct FixtureEntry: Codable {
  let sceneId: String
  let file: String
  let fixtureSet: String        // calibration | validation | holdout
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

  struct SplitDeclaration: Codable {
    let calibration: [String]
    let validation: [String]
    let holdout: [String]
    let note: String
  }
}

enum Environment {
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
