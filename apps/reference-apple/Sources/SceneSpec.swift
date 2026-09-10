import Foundation
import CoreGraphics
import SwiftUI

/// The decoded form of `scenes.json`.
///
/// Deliberately a mirror of the file rather than a richer model: the file is the
/// contract shared with the web side, so anything this type infers that the file
/// does not state would be a divergence waiting to happen. `$comment` keys decode
/// away for free — `Codable` ignores unknown keys.

struct CanvasSize: Decodable {
  let width: Double
  let height: Double
  var cgSize: CGSize { CGSize(width: width, height: height) }
}

/// Backgrounds are a closed set of generators, not arbitrary art, because both
/// renderers must produce the *same* raster and only a generator can promise that.
enum BackgroundSpec {
  case solid(srgb: [Int])
  case checkerboard(cell: Double, a: [Int], b: [Int])
  case impulse(background: [Int], foreground: [Int], size: Double, spacing: Double)
  case syntheticPhoto(seed: Int)
  case textRows(background: [Int], foreground: [Int], rowHeight: Double, barHeight: Double)
}

extension BackgroundSpec: Decodable {
  private enum CodingKeys: String, CodingKey {
    case kind, srgb, cell, a, b, background, foreground, size, spacing, seed, rowHeight, barHeight
  }

  init(from decoder: Decoder) throws {
    let c = try decoder.container(keyedBy: CodingKeys.self)
    let kind = try c.decode(String.self, forKey: .kind)
    switch kind {
    case "solid":
      self = .solid(srgb: try c.decode([Int].self, forKey: .srgb))
    case "checkerboard":
      self = .checkerboard(cell: try c.decode(Double.self, forKey: .cell),
                           a: try c.decode([Int].self, forKey: .a),
                           b: try c.decode([Int].self, forKey: .b))
    case "impulse":
      self = .impulse(background: try c.decode([Int].self, forKey: .background),
                      foreground: try c.decode([Int].self, forKey: .foreground),
                      size: try c.decode(Double.self, forKey: .size),
                      spacing: try c.decode(Double.self, forKey: .spacing))
    case "synthetic-photo":
      self = .syntheticPhoto(seed: try c.decode(Int.self, forKey: .seed))
    case "text-rows":
      self = .textRows(background: try c.decode([Int].self, forKey: .background),
                       foreground: try c.decode([Int].self, forKey: .foreground),
                       rowHeight: try c.decode(Double.self, forKey: .rowHeight),
                       barHeight: try c.decode(Double.self, forKey: .barHeight))
    default:
      throw DecodingError.dataCorruptedError(forKey: .kind, in: c,
        debugDescription: "unknown background kind '\(kind)' — the generator set is closed on purpose")
    }
  }
}

/// A shape, in the two families v1 calibrates (X8's uniform-radii restriction holds).
struct ShapeSpec: Decodable {
  let kind: String          // "capsule" | "rrect"
  let size: [Double]
  let radius: Double?
  let offset: [Double]?

  var cgSize: CGSize { CGSize(width: size[0], height: size[1]) }
  var cgOffset: CGSize { CGSize(width: offset?[0] ?? 0, height: offset?[1] ?? 0) }
}

enum ComponentSpec {
  case shape(ShapeSpec)
  case group(items: [ShapeSpec], spacing: Double)
  case stack(base: ShapeSpec, over: ShapeSpec)
}

extension ComponentSpec: Decodable {
  private enum CodingKeys: String, CodingKey {
    case kind, size, radius, offset, items, spacing, base, over
  }

  init(from decoder: Decoder) throws {
    let c = try decoder.container(keyedBy: CodingKeys.self)
    let kind = try c.decode(String.self, forKey: .kind)
    switch kind {
    case "capsule", "rrect":
      self = .shape(try ShapeSpec(from: decoder))
    case "group":
      self = .group(items: try c.decode([ShapeSpec].self, forKey: .items),
                    spacing: try c.decode(Double.self, forKey: .spacing))
    case "stack":
      self = .stack(base: try c.decode(ShapeSpec.self, forKey: .base),
                    over: try c.decode(ShapeSpec.self, forKey: .over))
    default:
      throw DecodingError.dataCorruptedError(forKey: .kind, in: c,
        debugDescription: "unknown component kind '\(kind)'")
    }
  }
}

/// An author tint, as `Glass.tint(_:)` takes it. sRGB components 0…255 and an
/// optional alpha, which is the tint's STRENGTH on both sides: SwiftUI's
/// `Color.opacity` and vitrea's colour-alpha are the same axis.
struct TintSpec: Decodable {
  let srgb: [Int]
  let alpha: Double?

  /// `Color(.sRGB, …)` explicitly rather than `Color(red:green:blue:)`: the whole
  /// pipeline is sRGB-locked (X5) and the capture's observed colour space is
  /// `kCGColorSpaceSRGB`, so the one place a colour enters the native side should
  /// name the space rather than inherit a default.
  var color: Color {
    Color(.sRGB,
          red:     Double(srgb[0]) / 255,
          green:   Double(srgb[1]) / 255,
          blue:    Double(srgb[2]) / 255,
          opacity: alpha ?? 1)
  }
}

struct SceneEntry: Decodable {
  let id: String
  let background: String
  let component: String
  let state: String
  /// Absent on every scene that predates W3, which is what keeps the existing
  /// bed byte-identical: no tint declared, no `.tint(_:)` applied.
  let tint: String?
}

/// Which scenes a profile captures: every scene, or a named subset.
enum ProfileScenes: Decodable {
  case all
  case some([String])

  init(from decoder: Decoder) throws {
    let single = try decoder.singleValueContainer()
    if let s = try? single.decode(String.self) {
      guard s == "all" else {
        throw DecodingError.dataCorruptedError(in: single,
          debugDescription: "profile.scenes must be \"all\" or a list of scene ids, got '\(s)'")
      }
      self = .all
    } else {
      self = .some(try single.decode([String].self))
    }
  }
}

struct ProfileSpec: Decodable {
  let key: String
  let colorScheme: String   // "light" | "dark"
  let a11y: String          // "standard" | "reduced-transparency" | "increased-contrast"
  let scenes: ProfileScenes
}

struct SplitSpec: Decodable {
  let holdout: [String]
  let validation: [String]
  let calibration: [String]
  /// Captured and committed, read by nothing. Optional so a spec file written
  /// before the role existed still decodes; absent means the list is empty.
  let recorded: [String]?
  /// Captured routinely and read by fits and claims, but gated by nothing —
  /// W25's fifth role (Decision Log 3 (e)). It is the opposite of `recorded` in
  /// what may read it and the same in what may bind to it: no adopted bound,
  /// regression floor or conditioning exclusion is stated over a probe cell, so
  /// the frozen bed's gate does not move when this list grows. Optional for the
  /// same reason `recorded` is.
  let probe: [String]?

  /// Which role a scene holds. An unassigned scene is a spec bug, not a
  /// default — a scene silently treated as `calibration` is exactly how a
  /// holdout leaks into tuning.
  ///
  /// `recorded` and `probe` are checked first because they are the roles that
  /// *remove* a scene from the gated sets, and a scene that has been retired
  /// from tuning — or that was never in the frozen bed to begin with — must not
  /// keep a gated membership by being named twice.
  func set(for sceneId: String) -> String? {
    if (recorded ?? []).contains(sceneId) { return "recorded" }
    if (probe ?? []).contains(sceneId) { return "probe" }
    if holdout.contains(sceneId) { return "holdout" }
    if validation.contains(sceneId) { return "validation" }
    if calibration.contains(sceneId) { return "calibration" }
    return nil
  }
}

struct SceneSpecFile: Decodable {
  let version: Int
  let canvas: CanvasSize
  let backgrounds: [String: BackgroundSpec]
  let components: [String: ComponentSpec]
  /// W3's author-tint registry, declared beside `backgrounds` and `components`
  /// rather than smuggled into either. Optional so a spec file that predates W3
  /// still decodes.
  let tints: [String: TintSpec]?
  let scenes: [SceneEntry]
  let profiles: [ProfileSpec]
  let split: SplitSpec

  func scenes(for profile: ProfileSpec) -> [SceneEntry] {
    switch profile.scenes {
    case .all: return scenes
    case .some(let ids): return scenes.filter { ids.contains($0.id) }
    }
  }

  /// Fail loudly at load if the split does not cover the matrix. This is the one
  /// invariant that cannot be checked later: by the time C9 is tuning, an
  /// unassigned scene looks like any other input.
  func validate() throws {
    var problems: [String] = []
    let ids = Set(scenes.map(\.id))
    for s in scenes where split.set(for: s.id) == nil {
      problems.append("scene '\(s.id)' is in no split set")
    }
    let declared = split.holdout + split.validation + split.calibration
      + (split.recorded ?? []) + (split.probe ?? [])
    for id in declared where !ids.contains(id) {
      problems.append("split names '\(id)', which is not a scene")
    }
    // A scene in two lists has two roles, and `set(for:)` would silently return
    // whichever it checks first. That is the same class of bug as an unassigned
    // scene — a role decided by the order of an if-chain rather than by the
    // declaration — and it became reachable the moment a fourth role existed to
    // move a scene INTO while its old membership stayed behind.
    var seen: [String: String] = [:]
    for (role, list) in [("calibration", split.calibration), ("validation", split.validation),
                         ("holdout", split.holdout), ("recorded", split.recorded ?? []),
                         ("probe", split.probe ?? [])] {
      for id in list {
        if let already = seen[id] { problems.append("scene '\(id)' is in both '\(already)' and '\(role)'") }
        else { seen[id] = role }
      }
    }
    for s in scenes {
      if backgrounds[s.background] == nil { problems.append("scene '\(s.id)': no background '\(s.background)'") }
      if components[s.component] == nil { problems.append("scene '\(s.id)': no component '\(s.component)'") }
      // A scene naming a tint the registry does not hold must fail HERE. The
      // resolution at the capture call site is a dictionary lookup, so an
      // unknown id would otherwise resolve to nil and file a silently untinted
      // capture under a tinted scene id — the one failure mode that puts an
      // untinted cell into a tinted matrix with nothing in the bytes to say so.
      if let t = s.tint, tints?[t] == nil { problems.append("scene '\(s.id)': no tint '\(t)'") }
    }
    for (id, t) in (tints ?? [:]) where t.srgb.count != 3 {
      problems.append("tint '\(id)': srgb must have 3 components, got \(t.srgb.count)")
    }
    for p in profiles {
      if case .some(let want) = p.scenes {
        for id in want where !ids.contains(id) {
          problems.append("profile '\(p.key)' names scene '\(id)', which does not exist")
        }
      }
    }
    guard problems.isEmpty else {
      throw NSError(domain: "vitrea.scenespec", code: 1,
                    userInfo: [NSLocalizedDescriptionKey: "scenes.json is inconsistent:\n  - " + problems.joined(separator: "\n  - ")])
    }
  }

  static func load(_ path: String) throws -> SceneSpecFile {
    let data = try Data(contentsOf: URL(fileURLWithPath: path))
    let spec = try JSONDecoder().decode(SceneSpecFile.self, from: data)
    try spec.validate()
    return spec
  }

  /// The `state` values a fresh run of this harness can put on screen and
  /// capture: the two interaction poses `SceneView` and `Capture` actually
  /// reach. `"inactive"` names the window-recede pose (W27c; claims §5.128,
  /// §5.130) — a real scene state, not a capture technique, and this harness
  /// has no way to put its OWN window into it: `Capture.present` activates and
  /// key-focuses the window on every path, and nothing here can ask AppKit for
  /// the opposite. W27c G2 lands vitrea's WEB runtime activation observer
  /// (`setWindowActivation`, the root option, the React prop) — it implements
  /// no native, capture-side deactivation, and no gate for one is chartered
  /// yet; that is separate work this harness does not do today. The 121
  /// inactive fixtures already on disk are recovered from the tree before the
  /// harness's window could ever become key (973fd7e^) — historical reference
  /// data, not something this run could reproduce by capturing again.
  static let freshlyCapturableStates: Set<String> = ["rest", "pressed"]

  /// Which of `ids` name a scene whose declared `state` a fresh run cannot
  /// reproduce, per `freshlyCapturableStates`. An id this spec does not
  /// recognize is left out — that is `validate()`'s failure to report, not
  /// this one's.
  ///
  /// Pure: reads only the already-decoded spec, touches no disk and opens no
  /// window, so a capture or layer-dump path can call it before either does
  /// anything a refusal would need to undo. General scene lookups — the
  /// calibration package's own loaders, `probe`, `tint-doctor` — read every
  /// state as valid reference data and must not call this; `validate()` above
  /// is the only gate they need to pass.
  func scenesUnsupportedForFreshCapture<S: Sequence>(_ ids: S) -> [String] where S.Element == String {
    let byId = Dictionary(uniqueKeysWithValues: scenes.map { ($0.id, $0) })
    return ids
      .filter { id in
        guard let scene = byId[id] else { return false }
        return !SceneSpecFile.freshlyCapturableStates.contains(scene.state)
      }
      .sorted()
  }
}
