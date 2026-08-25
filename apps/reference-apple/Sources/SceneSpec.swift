import Foundation
import CoreGraphics

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

struct SceneEntry: Decodable {
  let id: String
  let background: String
  let component: String
  let state: String
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

  /// Which set a scene belongs to. An unassigned scene is a spec bug, not a
  /// default — a scene silently treated as `calibration` is exactly how a
  /// holdout leaks into tuning.
  func set(for sceneId: String) -> String? {
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
    for id in split.holdout + split.validation + split.calibration where !ids.contains(id) {
      problems.append("split names '\(id)', which is not a scene")
    }
    for s in scenes {
      if backgrounds[s.background] == nil { problems.append("scene '\(s.id)': no background '\(s.background)'") }
      if components[s.component] == nil { problems.append("scene '\(s.id)': no component '\(s.component)'") }
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
}
