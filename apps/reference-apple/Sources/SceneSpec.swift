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
  case linearGradient(from: [Int], to: [Int], angle: Double)
  case split(from: [Int], to: [Int], axis: String, position: Double)
  case checkerboard(cell: Double, a: [Int], b: [Int])
  case impulse(background: [Int], foreground: [Int], size: Double, spacing: Double)
  case syntheticPhoto(seed: Int)
  case textRows(background: [Int], foreground: [Int], rowHeight: Double, barHeight: Double)
}

extension BackgroundSpec: Decodable {
  private enum CodingKeys: String, CodingKey {
    case kind, srgb, cell, a, b, background, foreground, size, spacing, seed, rowHeight, barHeight
    case from, to, angle, axis, position
  }

  init(from decoder: Decoder) throws {
    let c = try decoder.container(keyedBy: CodingKeys.self)
    let kind = try c.decode(String.self, forKey: .kind)
    switch kind {
    case "solid":
      self = .solid(srgb: try c.decode([Int].self, forKey: .srgb))
    case "linear-gradient", "split":
      let from = try c.decode([Int].self, forKey: .from)
      let to = try c.decode([Int].self, forKey: .to)
      guard [from, to].allSatisfy({ $0.count == 3 && $0.allSatisfy({ (0...255).contains($0) }) }) else {
        throw DecodingError.dataCorruptedError(forKey: .from, in: c,
          debugDescription: "gradient/split endpoints must be three sRGB bytes")
      }
      if kind == "linear-gradient" {
        let angle = try c.decode(Double.self, forKey: .angle)
        self = .linearGradient(from: from, to: to, angle: angle)
      } else {
        let axis = try c.decode(String.self, forKey: .axis)
        guard axis == "x" || axis == "y" else {
          throw DecodingError.dataCorruptedError(forKey: .axis, in: c,
            debugDescription: "split axis must be x or y")
        }
        self = .split(from: from, to: to, axis: axis,
                      position: try c.decode(Double.self, forKey: .position))
      }
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

/// A supplied shape. Circular capsules are a probe control beside the existing continuous paths.
struct ShapeSpec: Decodable {
  let kind: String          // "capsule" | "capsule-circular" | "rrect"
  let size: [Double]
  let radius: Double?
  let offset: [Double]?
  /// The shape's CENTRE in canvas CSS px, image-down (W39, X11). Mutually
  /// exclusive with `offset`, and rendered as a LAYOUT placement
  /// (`.position(x:y:)`) rather than a render-time translation: W34 measured that
  /// `.offset` snaps a fractional translation to two states (§5.174), and a bed
  /// that pins a near edge at a fractional coordinate (position = edge + size/2)
  /// cannot be built on a displacement the window server rounds. Absent on every
  /// scene that predates W39, whose placement is therefore unchanged.
  let position: [Double]?
  /// An ordinary opaque fill, never a material. Keeping the control on the same
  /// shape spec guarantees it resolves the same supplied path as its glass twin.
  let opaque: Bool?
  let fillSRGB: [Int]?

  var cgSize: CGSize { CGSize(width: size[0], height: size[1]) }
  var cgOffset: CGSize { CGSize(width: offset?[0] ?? 0, height: offset?[1] ?? 0) }
  var cgPosition: CGPoint? { position.map { CGPoint(x: $0[0], y: $0[1]) } }

  /// The frame this shape is placed at, in canvas CSS px, image-down — the one
  /// computation both the view and the path attestation read, so the attested
  /// `frameOrigin` cannot drift from the placement that was rendered. A
  /// positioned shape's origin is its centre minus half its size, exactly, with
  /// no rounding at any size; an unpositioned one is centred plus its offset, as
  /// every scene before W39 always was.
  func frame(in canvas: CGSize) -> CGRect {
    let origin: CGPoint
    if let p = cgPosition {
      origin = CGPoint(x: p.x - size[0] / 2, y: p.y - size[1] / 2)
    } else {
      origin = CGPoint(x: (canvas.width - size[0]) / 2 + cgOffset.width,
                       y: (canvas.height - size[1]) / 2 + cgOffset.height)
    }
    return CGRect(origin: origin, size: cgSize)
  }
}

enum ComponentSpec {
  case none
  case shape(ShapeSpec)
  case group(items: [ShapeSpec], spacing: Double)
  case stack(base: ShapeSpec, over: ShapeSpec)
  /// W39's two INDEPENDENT surfaces in one window (X11): each member its own
  /// `glassEffect` (or its own opaque fill), each placed by its own `position`,
  /// in no `GlassEffectContainer` and not the `stack`, whose upper surface
  /// samples the lower one. The column exists to test whether the body law is
  /// constant against window height with two bodies that share nothing but the
  /// window, so anything that could couple them — a container's merge, one
  /// surface drawn over the other, overlapping frames — is refused at load.
  case column(items: [ShapeSpec])
}

extension ComponentSpec: Decodable {
  private enum CodingKeys: String, CodingKey {
    case kind, size, radius, offset, items, spacing, base, over
  }

  init(from decoder: Decoder) throws {
    let c = try decoder.container(keyedBy: CodingKeys.self)
    let kind = try c.decode(String.self, forKey: .kind)
    switch kind {
    case "capsule", "capsule-circular", "rrect":
      self = .shape(try ShapeSpec(from: decoder))
    case "none": self = .none
    case "group":
      self = .group(items: try c.decode([ShapeSpec].self, forKey: .items),
                    spacing: try c.decode(Double.self, forKey: .spacing))
    case "stack":
      self = .stack(base: try c.decode(ShapeSpec.self, forKey: .base),
                    over: try c.decode(ShapeSpec.self, forKey: .over))
    case "column":
      self = .column(items: try c.decode([ShapeSpec].self, forKey: .items))
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

/// A text label rendered INSIDE the glass — for the layer dump only.
///
/// The no-text rule in `SceneViews.swift` is why the fixtures are trustworthy: a
/// glyph rasteriser inside the region being measured puts two different renderers'
/// antialiasing on the material axis. Nothing here weakens it. A label is declared
/// only in a probe spec, `capture` refuses any scene that declares one before a
/// window opens, and `dump-layers` — which reads a configuration and captures no
/// pixels — is the only path that renders it.
///
/// It exists because claims §5.133 §2 found that the committed corpus contains no
/// label's vibrancy operator at all, for exactly this reason: "the reference
/// harness renders `Color.clear` inside every `glassEffect` by an explicit rule".
/// §5.133 §7 names the one run that would answer it, and §8 (c) makes it the open
/// question W27e G1 cannot fit around.
struct LabelSpec: Decodable {
  let text: String
  /// sRGB 0…255. Absent means `Color.primary` — the AUTOMATIC label colour, which
  /// is the case S284 describes ("the label automatically becomes vibrant, based
  /// on its textColor") and the one the dump is being taken to read.
  let srgb: [Int]?
  /// Point size. Declared rather than defaulted in the view, because a dump that
  /// is compared across scenes must not have a font size that varies with
  /// anything; 15 is the system body size Apple's own controls use.
  let fontSize: Double?

  var color: Color? {
    guard let srgb, srgb.count == 3 else { return nil }
    return Color(.sRGB, red: Double(srgb[0]) / 255, green: Double(srgb[1]) / 255,
                 blue: Double(srgb[2]) / 255, opacity: 1)
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
  /// Absent on every scene in `scenes.json`, and on every scene any capture path
  /// will accept. See `LabelSpec`.
  let label: LabelSpec?
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
    for s in scenes {
      guard let label = s.label else { continue }
      if label.text.isEmpty { problems.append("scene '\(s.id)': label.text is empty") }
      if let srgb = label.srgb, srgb.count != 3 {
        problems.append("scene '\(s.id)': label.srgb must have 3 components, got \(srgb.count)")
      }
      // Only a single shape carries one. `SceneView` puts the label inside the
      // `glassEffect`, and for a group or a stack "inside" names several
      // surfaces — a dump of which would not say which one the operator sat on,
      // which is the entire question. Refused rather than silently dropped.
      if case .shape = components[s.component] {} else {
        problems.append("scene '\(s.id)': a label may only be declared on a single-shape component")
      }
    }
    func validateShape(_ s: ShapeSpec, _ id: String) {
      if !["capsule", "capsule-circular", "rrect"].contains(s.kind)
          || s.size.count != 2 || !s.size.allSatisfy({ $0.isFinite && $0 > 0 }) {
        problems.append("component '\(id)': invalid shape kind or size")
      }
      if let offset = s.offset, offset.count != 2 || !offset.allSatisfy({ $0.isFinite }) {
        problems.append("component '\(id)': offset must be two finite CSS lengths")
      }
      problems += positionProblems(s, id)
      if s.opaque == true {
        guard let rgb = s.fillSRGB, rgb.count == 3,
              rgb.allSatisfy({ (0...255).contains($0) }) else {
          problems.append("component '\(id)': opaque control needs three fillSRGB bytes")
          return
        }
      } else if s.fillSRGB != nil {
        problems.append("component '\(id)': fillSRGB requires opaque true")
      }
    }
    for (id, component) in components {
      switch component {
      case .none: break
      case .shape(let shape): validateShape(shape, id)
      case .group(let items, _):
        for shape in items { validateShape(shape, id) }
        if items.contains(where: { $0.opaque == true }) {
          problems.append("component '\(id)': opaque controls require a single shape")
        }
        // A group is laid out by its container's HStack and a stack's base is
        // centred, so a `position` on either would be decoded and then ignored —
        // a declared placement that is not the rendered one. Refused instead.
        if items.contains(where: { $0.position != nil }) {
          problems.append("component '\(id)': position is not honoured inside a group")
        }
      case .stack(let base, let over):
        validateShape(base, id); validateShape(over, id)
        if base.opaque == true || over.opaque == true {
          problems.append("component '\(id)': opaque controls require a single shape")
        }
        if base.position != nil || over.position != nil {
          problems.append("component '\(id)': position is not honoured inside a stack")
        }
      case .column(let items):
        for shape in items { validateShape(shape, id) }
        problems += columnProblems(items, id)
      }
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

  /// A `position` is two finite CSS coordinates, never beside an `offset`, and
  /// far enough inside the canvas that the whole shape is: the centre lies within
  /// the canvas shrunk by half the shape's size on each axis. The bound is on the
  /// SHAPE's frame, not its outer shadow; what the exterior reader needs beyond
  /// it is the declaration's margin to state, not this loader's.
  func positionProblems(_ s: ShapeSpec, _ id: String) -> [String] {
    guard let p = s.position else { return [] }
    var problems: [String] = []
    if s.offset != nil {
      problems.append("component '\(id)': position and offset are mutually exclusive")
    }
    guard p.count == 2, p.allSatisfy({ $0.isFinite }) else {
      return problems + ["component '\(id)': position must be two finite CSS coordinates"]
    }
    guard s.size.count == 2, s.size.allSatisfy({ $0.isFinite && $0 > 0 }) else { return problems }
    let half = [s.size[0] / 2, s.size[1] / 2]
    let extent = [canvas.width, canvas.height]
    for axis in 0..<2 where p[axis] < half[axis] || p[axis] > extent[axis] - half[axis] {
      problems.append("component '\(id)': position \(p) puts the \(s.size[0])×\(s.size[1]) " +
                      "shape outside the \(canvas.width)×\(canvas.height) canvas")
      break
    }
    return problems
  }

  /// A column is exactly two members, each placed by its own `position`, both
  /// glass or both opaque (the two-fill control), whose frames do not overlap.
  /// Frames that only share an edge do not overlap: the intersection must have
  /// positive area on both axes to be refused.
  func columnProblems(_ items: [ShapeSpec], _ id: String) -> [String] {
    var problems: [String] = []
    guard items.count == 2 else {
      return ["component '\(id)': a column has exactly two members, got \(items.count)"]
    }
    if items.contains(where: { $0.position == nil }) {
      problems.append("component '\(id)': every column member needs a position")
    }
    if (items[0].opaque == true) != (items[1].opaque == true) {
      problems.append("component '\(id)': a column is two glass surfaces or two opaque fills")
    }
    guard problems.isEmpty,
          items.allSatisfy({ $0.size.count == 2 && $0.position?.count == 2 }) else { return problems }
    let a = items[0].frame(in: canvas.cgSize), b = items[1].frame(in: canvas.cgSize)
    if a.minX < b.maxX && b.minX < a.maxX && a.minY < b.maxY && b.minY < a.maxY {
      problems.append("component '\(id)': the column members' frames \(a) and \(b) overlap")
    }
    return problems
  }

  static func load(_ path: String) throws -> SceneSpecFile {
    let data = try Data(contentsOf: URL(fileURLWithPath: path))
    let spec = try JSONDecoder().decode(SceneSpecFile.self, from: data)
    try spec.validate()
    return spec
  }

  /// The `state` values a fresh run of this harness can put on screen and
  /// capture, PER PRESENTATION POSE.
  ///
  /// The two sets are disjoint, and that is the point: a run presents one pose
  /// for its whole length, so the states it can reach are decided once, and a
  /// scene whose state belongs to the other pose is refused before a window
  /// opens rather than captured under the wrong appearance.
  ///
  /// `.active` reaches `"rest"` and `"pressed"` — the two interaction poses
  /// `SceneView` renders, under `Capture.present`, which activates and
  /// key-focuses. `.inactive` reaches `"inactive"` alone, the window-recede pose
  /// W27c measures (claims §5.128, §5.130), under `Capture.presentInactive`.
  /// The recede is a pose of the PRESENTATION, not of the scene's content, so
  /// nothing in the view hierarchy differs between the two and only the
  /// per-cell attestation can tell a bed which one it holds.
  ///
  /// Until 2026-09-11 the inactive side did not exist: `Capture.present`
  /// activated on every path and the 121 inactive fixtures on disk were
  /// recovered from the tree before this harness's window could ever become key
  /// (`973fd7e^`) rather than captured. `presentInactive` is that path, built
  /// for the checking bed of claims §5.134 §5 under W27 Decision Log 13. It is
  /// still not vitrea's WEB runtime activation observer, which is W27c G2 and
  /// is held.
  static func freshlyCapturableStates(for pose: CapturePose) -> Set<String> {
    switch pose {
    case .active: return ["rest", "pressed"]
    case .inactive: return ["inactive"]
    }
  }

  /// Which of `ids` declare a label, and so may never be captured at all.
  ///
  /// Separate from the pose check, and checked separately, because it is a
  /// different rule with a different reason. A pose is reproducible in the right
  /// run; a labelled scene is reproducible in NO capture run, in either pose, at
  /// any scale, ever — the no-text fixture rule is what makes the material
  /// measurement a measurement of the material.
  func scenesDeclaringALabel<S: Sequence>(_ ids: S) -> [String] where S.Element == String {
    let byId = Dictionary(uniqueKeysWithValues: scenes.map { ($0.id, $0) })
    return ids.filter { byId[$0]?.label != nil }.sorted()
  }

  /// Which of `ids` name a scene whose declared `state` a fresh run in this pose
  /// cannot reproduce. An id this spec does not recognize is left out — that is
  /// `validate()`'s failure to report, not this one's.
  ///
  /// Pure: reads only the already-decoded spec, touches no disk and opens no
  /// window, so a capture or layer-dump path can call it before either does
  /// anything a refusal would need to undo. General scene lookups — the
  /// calibration package's own loaders, `probe`, `tint-doctor` — read every
  /// state as valid reference data and must not call this; `validate()` above
  /// is the only gate they need to pass.
  func scenesUnsupportedForFreshCapture<S: Sequence>(
    _ ids: S, pose: CapturePose = .active
  ) -> [String] where S.Element == String {
    let reachable = SceneSpecFile.freshlyCapturableStates(for: pose)
    let byId = Dictionary(uniqueKeysWithValues: scenes.map { ($0.id, $0) })
    return ids
      .filter { id in
        guard let scene = byId[id] else { return false }
        return !reachable.contains(scene.state)
      }
      .sorted()
  }
}
