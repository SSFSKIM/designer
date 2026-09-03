import Foundation
import AppKit
import QuartzCore
import ObjectiveC.runtime

/// Read Apple's own Liquid Glass parameters out of SwiftUI's Core Animation
/// layer tree.
///
/// The calibration bed measures the material from the outside: it photographs
/// what the window server composited and fits constants until the pixels agree.
/// That works, but it can only ever say *a* parameterisation reproduces the
/// image, never that it is *the* one. The material itself is configured by
/// ordinary Core Animation objects — a `CABackdropLayer` carrying a `CAFilter`
/// whose input keys are the blur radii, refraction amounts, face opacities and
/// colour matrices — and those objects are readable from inside the process that
/// hosts the view. Reading them turns a fit into a comparison against the
/// reference implementation's declared numbers.
///
/// Everything here is discovery, not assertion. The class and key names differ
/// between OS builds and none of them are API, so the dump asks each object what
/// it has (`class_copyPropertyList`, `class_copyMethodList`) rather than asking
/// for names it expects to find. A name that is neither a declared property nor
/// a zero-argument method is never sent, so `NSUnknownKeyException` — which
/// Swift cannot catch and which would take the whole run down — has no way to
/// fire. Getters whose return type is not an object, a scalar or one of the
/// handful of geometry structs Key-Value Coding knows how to box are skipped for
/// the same reason.
///
/// This is local interoperability research on one machine. Nothing here is
/// compiled into anything that ships, and no fixture, scene or manifest is
/// touched by it.
enum LayerDump {

  /// Every reflected read, announced before it happens, when
  /// `VITREA_DUMP_TRACE=1` is set.
  ///
  /// A getter that blocks or spins takes the whole dump with it and leaves no
  /// record of which one it was, because the run is walking classes nobody
  /// documented. The trace is the only way to name the culprit, and it is off by
  /// default because it is one line per property per object.
  nonisolated(unsafe) private static let trace =
    ProcessInfo.processInfo.environment["VITREA_DUMP_TRACE"] == "1"

  /// `readableNames(of:)` walks a class chain and copies two runtime lists per
  /// class; the same dozen classes recur on every layer of every scene, so the
  /// answer is memoised. Without this the walk is quadratic in a tree that has
  /// hundreds of nodes and each class has hundreds of zero-argument methods.
  nonisolated(unsafe) private static var nameCache: [ObjectIdentifier: [String]] = [:]

  // MARK: - Reflection safety

  /// Names that are readable but must not be read.
  ///
  /// Three different reasons, all of which end the run rather than produce a
  /// line of output: the memory-management prefixes (`new`, `copy`, `init`, …)
  /// confuse ARC about ownership of what Key-Value Coding hands back; the tree
  /// links (`superlayer`, `presentationLayer`, `modelLayer`) walk back up or
  /// sideways into a cycle; and `contents` is an `IOSurface` or `CGImage` whose
  /// description is megabytes of nothing.
  private static let deniedNames: Set<String> = [
    "superlayer", "presentationLayer", "modelLayer", "sublayers", "contents",
    "delegate", "mask", "description", "debugDescription", "hash", "superclass",
    "self", "zone", "observationInfo", "filters", "backgroundFilters",
    "compositingFilter", "nextResponder", "window", "superview", "subviews",
    "class",
  ]

  private static let deniedPrefixes = [
    "_alloc", "alloc", "new", "copy", "mutableCopy", "init", "dealloc",
    "retain", "release", "autorelease", "finalize", "accessibility",
  ]

  /// Whether a getter's return type is one Key-Value Coding can box safely.
  ///
  /// KVC boxes scalars into `NSNumber` and a fixed set of geometry structs into
  /// `NSValue` using the method's Objective-C type encoding. For anything else —
  /// a bare pointer, a `void` return, an unknown struct — it either raises or
  /// reads the wrong number of bytes off the stack, so those getters are simply
  /// not called.
  private static func encodingIsSafe(_ encoding: String) -> Bool {
    if encoding == "@" { return true }                       // object, but not a block ("@?")
    if encoding.count == 1, "cislqCISLQfdB".contains(encoding) { return true }
    for known in ["{CGRect", "{CGPoint", "{CGSize", "{CGAffineTransform",
                  "{CATransform3D", "{NSRect", "{NSPoint", "{NSSize", "{_NSRange"] {
      if encoding.hasPrefix(known) { return true }
    }
    return false
  }

  private static func nameIsSafe(_ name: String) -> Bool {
    if deniedNames.contains(name) { return false }
    for p in deniedPrefixes where name.hasPrefix(p) { return false }
    return true
  }

  /// Every key that can be read off this class and its superclasses, stopping
  /// at `CALayer` (and below `NSObject` for everything else) so the dump reports
  /// what the private subclass added rather than the universal plumbing.
  ///
  /// Both halves of the Objective-C surface are consulted, because a private
  /// class often exposes its interesting state as a bare getter with no
  /// `@property` declaration at all — the `CASDF…` effect objects are exactly
  /// that shape.
  ///
  /// Stopping at `CALayer` is not only about noise, and the reason is the single
  /// most surprising thing this file learned. `CALayer`'s selector list is not
  /// `CALayer`'s: every framework loaded into the process bolts categories onto
  /// it, and some of those category getters are lazy *constructors*. MapKit's
  /// `vk_autoFadeOutShapeRectLayer` builds a `VKAutoFadeOutLayer` and inserts it
  /// as a sublayer of the receiver, so a walk that reads it grows the very tree
  /// it is walking — measured 2026-09-03 at 12254 layers and 2.7 million reads
  /// before the run was killed. The stock geometry is recorded explicitly in
  /// `describeLayer` instead, which is the part of `CALayer` anyone wanted.
  private static func readableNames(of cls: AnyClass) -> [String] {
    if let cached = nameCache[ObjectIdentifier(cls)] { return cached }
    var names = Set<String>()
    var current: AnyClass? = cls
    while let c = current, c !== NSObject.self, c !== CALayer.self {
      var count: UInt32 = 0
      if let props = class_copyPropertyList(c, &count) {
        for i in 0..<Int(count) {
          let p = props[i]
          let name = String(cString: property_getName(p))
          guard nameIsSafe(name) else { continue }
          if let attr = property_copyAttributeValue(p, "T") {
            defer { free(attr) }
            if encodingIsSafe(String(cString: attr)) { names.insert(name) }
          }
        }
        free(props)
      }
      count = 0
      if let methods = class_copyMethodList(c, &count) {
        for i in 0..<Int(count) {
          let m = methods[i]
          guard method_getNumberOfArguments(m) == 2 else { continue }   // self, _cmd only
          let name = String(cString: sel_getName(method_getName(m)))
          guard !name.contains(":"), nameIsSafe(name) else { continue }
          let ret = method_copyReturnType(m)
          defer { free(ret) }
          if encodingIsSafe(String(cString: ret)) { names.insert(name) }
        }
        free(methods)
      }
      current = class_getSuperclass(c)
    }
    let sorted = names.sorted()
    nameCache[ObjectIdentifier(cls)] = sorted
    return sorted
  }

  /// Whether an object reached through some other object's property is worth
  /// taking apart, or merely worth naming.
  ///
  /// The first version of this dump recursed into everything and did not finish:
  /// a `CALayer` answers several hundred zero-argument getters, a good number of
  /// them return objects that answer several hundred more, and three levels of
  /// that is not a file anyone would read even if it terminated. The material's
  /// parameters live in a narrow band of classes — the filters, the SDF effect
  /// objects, the glass descriptors — so those are opened and everything else is
  /// recorded by class and description, which is enough to notice that a name
  /// worth chasing was there.
  private static func isInteresting(_ cls: AnyClass) -> Bool {
    let name = NSStringFromClass(cls)
    for needle in ["SDF", "Effect", "Filter", "Glass", "Backdrop", "Material", "Descriptor"]
    where name.contains(needle) {
      return true
    }
    return false
  }

  // MARK: - Value rendering

  /// Render an arbitrary Objective-C value as something `JSONSerialization` will
  /// accept, recursing into nested objects up to `depth`.
  ///
  /// Colours are special-cased because they are the point: the glass filter's
  /// fill colour and the highlight effect's colour are `CGColor`s, and
  /// `String(describing:)` of one is an address. Everything else that is not a
  /// plist type is reported by its own description if the recursion budget is
  /// spent, which is still enough to see what class it was.
  private static func render(_ value: Any?, depth: Int) -> Any {
    guard let value else { return NSNull() }
    let object = value as AnyObject

    if CFGetTypeID(object) == CGColor.typeID {
      let color = object as! CGColor
      var out: [String: Any] = ["cgColorComponents": (color.components ?? []).map { Double($0) }]
      if let space = color.colorSpace, let name = space.name { out["colorSpace"] = name as String }
      return out
    }
    if let n = value as? NSNumber {
      let d = n.doubleValue
      return d.isFinite ? d : String(describing: n)
    }
    if let s = value as? String { return truncated(s) }
    if let a = value as? [Any] { return a.map { render($0, depth: depth) } }
    if let d = value as? [String: Any] {
      return d.mapValues { render($0, depth: depth) }
    }
    if let data = object as? NSData {
      // The colour matrices arrive as raw bytes. Left as a description they read
      // "{length = 80, bytes = 0x3ee8993f…}", which is the one form in which a
      // 5x4 matrix cannot be compared to anything; twenty floats can be.
      let count = data.length
      var out: [String: Any] = ["byteCount": Double(count)]
      if count % 4 == 0, count <= 1024 {
        let bytes = data.bytes.assumingMemoryBound(to: UInt8.self)
        var floats: [Double] = []
        for i in 0..<(count / 4) {
          var f: Float32 = 0
          memcpy(&f, bytes.advanced(by: i * 4), 4)
          floats.append(f.isFinite ? Double(f) : 0)
        }
        out["float32"] = floats
      }
      return out
    }
    if let v = value as? NSValue {
      // `objCType` is recorded rather than assumed: a boxed value whose struct
      // this dump does not recognise is still identifiable from its encoding.
      let encoding = String(cString: v.objCType)
      var out: [String: Any] = ["class": NSStringFromClass(type(of: v)),
                                "objCType": encoding,
                                "description": truncated(String(describing: v))]
      // A struct of nothing but floats — `{CAColorMatrix=ffffffffffffffffffff}`
      // is the 5x4 colour matrix, and it is the whole content of the
      // `vibrantColorMatrix` filter — is unboxed into its numbers. Anything else
      // keeps its description, which at least names the type that was there.
      if let open = encoding.firstIndex(of: "="), encoding.hasSuffix("}") {
        let fields = encoding[encoding.index(after: open)..<encoding.index(before: encoding.endIndex)]
        if !fields.isEmpty, fields.allSatisfy({ $0 == "f" }) {
          var buffer = [Float32](repeating: 0, count: fields.count)
          v.getValue(&buffer, size: MemoryLayout<Float32>.size * fields.count)
          out["float32"] = buffer.map { $0.isFinite ? Double($0) : 0 }
        }
      }
      return out
    }
    if let o = value as? NSObject {
      if depth > 0, isInteresting(type(of: o)) { return describe(o, depth: depth - 1) }
      return ["class": NSStringFromClass(type(of: o)),
              "description": truncated(String(describing: o))]
    }
    return truncated(String(describing: value))
  }

  /// Descriptions of layers and filters are the point of this dump, but a
  /// property that hands back a whole display list turns one into a megabyte.
  private static func truncated(_ s: String, limit: Int = 4000) -> String {
    s.count <= limit ? s : String(s.prefix(limit)) + "…[truncated \(s.count) chars]"
  }

  /// Whether an object is a value rather than a configuration: a string, a
  /// number, a boxed struct, a container.
  ///
  /// These must never be reflected over, and the reason is the `NSString` half of
  /// the lesson `readableNames(of:)` records. A `CALayer`'s `filters` array may
  /// hold a filter *name* instead of a `CAFilter` — the tinted scenes do exactly
  /// that — and `NSString` in a fully loaded application answers several thousand
  /// selectors bolted on by every framework in the process, many of which parse,
  /// allocate or hit the network. Reading them all is neither safe nor
  /// informative; the string itself is the whole content.
  private static func isValueLike(_ object: NSObject) -> Bool {
    object is NSString || object is NSNumber || object is NSValue
      || object is NSData || object is NSArray || object is NSDictionary || object is NSNull
  }

  /// Read every safely-readable key off an object.
  ///
  /// `responds(to:)` is checked again at the point of use even though the name
  /// came out of the runtime a moment ago: a class can answer a selector
  /// dynamically, and the cost of asking is nothing against the cost of a raised
  /// exception in a process with no way to catch one.
  private static func properties(of object: NSObject, depth: Int) -> [String: Any] {
    var out: [String: Any] = [:]
    guard !isValueLike(object) else { return out }
    for name in readableNames(of: type(of: object)) {
      guard object.responds(to: Selector(name)) else { continue }
      if trace {
        print("      · \(NSStringFromClass(type(of: object))).\(name)")
        fflush(stdout)
      }
      guard let raw = object.value(forKey: name) else { continue }
      out[name] = render(raw, depth: depth)
    }
    return out
  }

  /// A generic object record: class, its own description, and its readable state.
  ///
  /// The raw `description` is kept beside the parsed properties on purpose.
  /// `CAFilter` prints its inputs in its own description, so on a build where the
  /// key list is not reachable the string is the only record of what the filter
  /// was configured with — and a string that turned out to hold the answer is
  /// worth more than a tidier file.
  private static func describe(_ object: NSObject, depth: Int) -> [String: Any] {
    var out: [String: Any] = [
      "class": NSStringFromClass(type(of: object)),
      "description": truncated(String(describing: object)),
    ]
    let props = properties(of: object, depth: depth)
    if !props.isEmpty { out["properties"] = props }
    return out
  }

  // MARK: - Filters

  /// The input keys ShatteredGlass reports on `glassBackground`, used only as a
  /// fallback.
  ///
  /// A `CAFilter` normally answers `inputKeys` and the real key list is read
  /// from the object itself; this list exists for the case where it does not,
  /// and even then a key is only read after the object has confirmed it responds
  /// to a matching getter or has printed the name in its own description. The
  /// list is therefore a hint about where to look, never an assumption about
  /// what is there.
  private static let knownGlassInputKeys: [String] = [
    "inputBlurRadius", "inputBlurDistance0", "inputBlurDistance1", "inputBlurDistance2",
    "inputBlurDistance3", "inputBlurDistance4", "inputBlurOpacity0", "inputBlurOpacity1",
    "inputBlurOpacity2", "inputBlurOpacity3", "inputBlurOpacity4",
    "inputInnerRefractionAmount", "inputInnerRefractionHeight",
    "inputOuterRefractionAmount", "inputOuterRefractionHeight",
    "inputRefractionDistance0", "inputRefractionDistance1", "inputRefractionOpacity",
    "inputFaceOpacity", "inputFaceColorMatrixBlack", "inputFaceColorMatrixWhite",
    "inputFaceColorMatrixSaturation", "inputFaceColorMatrixFillColor",
    "inputBleedAmount", "inputBleedHeight", "inputBleedBlurRadius", "inputBleedOpacity",
    "inputBleedDistance0", "inputBleedDistance1", "inputBleedColorMatrixBlack",
    "inputBleedColorMatrixWhite", "inputBleedColorMatrixSaturation",
    "inputBleedColorMatrixFillColor",
    "inputShadowOffset", "inputShadowAmount", "inputShadowHeight",
    "inputShadowDistanceOffset", "inputShadowBlurRadius", "inputShadowRadius",
    "inputShadowOpacity", "inputShadowColorMatrixBlack", "inputShadowColorMatrixWhite",
    "inputShadowColorMatrixSaturation", "inputShadowColorMatrixFillColor",
    "inputShadowVibrancyContribution",
    "inputSDRHoldingToneEnabled", "inputMaxHeadroom",
    "inputSDRGradientDistance0", "inputSDRGradientDistance1", "inputSDRShadowOpacity",
    "inputSourceSublayerName",
  ]

  private static func describeFilter(_ filter: NSObject) -> [String: Any] {
    // A filter slot holding a bare name, not an object: recorded as what it is.
    if isValueLike(filter) {
      return ["kind": "filter", "class": NSStringFromClass(type(of: filter)),
              "value": render(filter, depth: 0)]
    }
    var out = describe(filter, depth: 2)
    out["kind"] = "filter"
    for key in ["type", "name"] where filter.responds(to: Selector(key)) {
      out[key] = render(filter.value(forKey: key), depth: 0)
    }

    // The object's own key list first. It is the only source that is right by
    // construction; everything below is a guess that has to be checked.
    var keys: [String] = []
    if filter.responds(to: Selector(("inputKeys"))),
       let declared = filter.value(forKey: "inputKeys") as? [String] {
      keys = declared
      out["inputKeysSource"] = "inputKeys"
    } else {
      let text = String(describing: filter) + (filter.debugDescription)
      keys = knownGlassInputKeys.filter {
        filter.responds(to: Selector($0)) || text.contains($0)
      }
      out["inputKeysSource"] = keys.isEmpty ? "none" : "known-list-confirmed"
    }

    var inputs: [String: Any] = [:]
    for key in keys {
      guard nameIsSafe(key) else { continue }
      // A declared input key is not necessarily a getter; `CAFilter` stores its
      // inputs in a dictionary and answers `valueForKey:` for them, so the
      // selector check cannot be required here. `inputKeys` having named the key
      // is itself the guarantee that asking for it is safe.
      inputs[key] = render(filter.value(forKey: key), depth: 2)
    }
    if !inputs.isEmpty { out["inputs"] = inputs }
    return out
  }

  // MARK: - The walk

  private static func describeLayer(_ layer: CALayer) -> [String: Any] {
    if trace { print("    layer \(NSStringFromClass(type(of: layer)))"); fflush(stdout) }
    var out: [String: Any] = [
      "class": NSStringFromClass(type(of: layer)),
      "name": layer.name ?? NSNull(),
      "frame": rect(layer.frame),
      "bounds": rect(layer.bounds),
      "position": ["x": Double(layer.position.x), "y": Double(layer.position.y)],
      "cornerRadius": Double(layer.cornerRadius),
      "cornerCurve": layer.cornerCurve.rawValue,
      "contentsScale": Double(layer.contentsScale),
      "opacity": Double(layer.opacity),
      "masksToBounds": layer.masksToBounds,
      "isHidden": layer.isHidden,
      "description": truncated(String(describing: layer)),
    ]
    if let c = layer.compositingFilter as? NSObject {
      out["compositingFilter"] = describeFilter(c)
    }
    if let f = layer.filters {
      out["filters"] = f.compactMap { ($0 as? NSObject).map(describeFilter) }
    }
    if let f = layer.backgroundFilters {
      out["backgroundFilters"] = f.compactMap { ($0 as? NSObject).map(describeFilter) }
    }
    // Snapshotted BEFORE the reflected read, for the same reason the class walk
    // stops at `CALayer`: a getter can add a sublayer, and a child that only
    // exists because the dump looked at its parent is not part of the tree
    // SwiftUI committed.
    let sublayers = layer.sublayers ?? []
    let props = properties(of: layer, depth: 1)
    if !props.isEmpty { out["properties"] = props }
    if !sublayers.isEmpty { out["sublayers"] = sublayers.map(describeLayer) }
    return out
  }

  private static func rect(_ r: CGRect) -> [String: Double] {
    ["x": Double(r.origin.x), "y": Double(r.origin.y),
     "width": Double(r.size.width), "height": Double(r.size.height)]
  }

  @MainActor
  static func describeView(_ view: NSView) -> [String: Any] {
    var out: [String: Any] = [
      "class": NSStringFromClass(type(of: view)),
      "frame": rect(view.frame),
      "wantsLayer": view.wantsLayer,
    ]
    if let layer = view.layer { out["layer"] = describeLayer(layer) }
    if !view.subviews.isEmpty { out["subviews"] = view.subviews.map(describeView) }
    return out
  }

  // MARK: - Summary

  /// Every object node in a dump, flattened, so the console summary can be
  /// produced from the same structure that was written to disk rather than from
  /// a second traversal that could disagree with it.
  static func nodes(in value: Any) -> [[String: Any]] {
    var found: [[String: Any]] = []
    if let dict = value as? [String: Any] {
      if dict["class"] is String { found.append(dict) }
      for (_, v) in dict { found.append(contentsOf: nodes(in: v)) }
    } else if let array = value as? [Any] {
      for v in array { found.append(contentsOf: nodes(in: v)) }
    }
    return found
  }

  static func printSummary(_ tree: [String: Any]) {
    let all = nodes(in: tree)
    var counts: [String: Int] = [:]
    for n in all { counts[n["class"] as? String ?? "?", default: 0] += 1 }
    print("  layer/object classes:")
    for (cls, n) in counts.sorted(by: { $0.key < $1.key }) { print("    \(n)x \(cls)") }

    for n in all where (n["kind"] as? String) == "filter" {
      let type = (n["type"] as? String) ?? (n["name"] as? String) ?? "?"
      let cls = n["class"] as? String ?? "?"
      guard let inputs = n["inputs"] as? [String: Any], !inputs.isEmpty else {
        print("  filter \(cls) type=\(type) — no readable inputs")
        continue
      }
      print("  filter \(cls) type=\(type):")
      for (k, v) in inputs.sorted(by: { $0.key < $1.key }) { print("    \(k) = \(compact(v))") }
    }

    for n in all {
      let cls = n["class"] as? String ?? ""
      guard cls.contains("Effect") || (cls.hasPrefix("CASDF") && !cls.hasSuffix("Layer")) else { continue }
      print("  effect \(cls):")
      if let props = n["properties"] as? [String: Any] {
        for (k, v) in props.sorted(by: { $0.key < $1.key }) { print("    \(k) = \(compact(v))") }
      }
    }
  }

  private static func compact(_ v: Any) -> String {
    if let d = v as? Double { return String(format: "%g", d) }
    if let dict = v as? [String: Any] {
      if let comps = dict["cgColorComponents"] as? [Double] {
        return "rgba(" + comps.map { String(format: "%.4f", $0) }.joined(separator: ", ") + ")"
      }
      if let cls = dict["class"] as? String { return "<\(cls)>" }
    }
    if let a = v as? [Any] { return "[" + a.map(compact).joined(separator: ", ") + "]" }
    if v is NSNull { return "nil" }
    return String(describing: v)
  }
}
