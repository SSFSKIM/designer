// W39 G0's non-GUI proof of the harness additions (X11, X25): load a scenes file through the
// harness's own loader — `SceneSpecFile.load`, which runs `validate()` and so refuses a
// `position` beside an `offset`, a shape outside the canvas and an overlapping column — then
// export every component's SUPPLIED paths exactly as the manifest records them and check each
// positioned shape's attestation against its declaration: the attested centre (frameOrigin +
// size/2) equals the declared `position`, the attested rect is the declared size unrounded,
// and the supplied path's own bounds are that rect. No window, no capture, no grant.
//
// It is compiled OUTSIDE the repository against the harness sources minus `main.swift` (this
// file carries the `@main`); `build.sh` and both protected bundles are never involved:
//
//   S=apps/reference-apple/Sources; OUT=~/vitrea-w39/scratch/export-paths
//   mkdir -p "$OUT" && xcrun swiftc -parse-as-library -swift-version 6 \
//     -target arm64-apple-macos26.0 -framework AppKit -framework ScreenCaptureKit \
//     -framework IOKit -o "$OUT/export-paths" \
//     $(ls "$S"/*.swift | grep -v '/main.swift$') \
//     packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed/export-paths.swift
//   "$OUT/export-paths" apps/reference-apple/scenes-w39-colour-edge.json \
//     > packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed/supplied-paths.json
//
// It exits 1 when any positioned shape's attestation differs from its declaration, so the
// committed JSON is the output of a passing run by construction.
import Foundation
import SwiftUI

struct PositionCheck: Encodable {
  let member: Int
  let kind: String
  let declaredPosition: [Double]
  let declaredSize: [Double]
  let frameOrigin: [Double]
  let attestedCentre: [Double]
  let rect: [Double]
  let pathBounds: [Double]
  let centreMatches: Bool
  let sizeMatches: Bool
  let pathBoundsMatch: Bool
}

struct Export: Encodable {
  let scenesFile: String
  let canvas: [Double]
  let components: [String: [SuppliedShapePath]]
  let positionChecks: [String: [PositionCheck]]
  let positionedShapes: Int
  let allMatch: Bool
}

// `TintDoctor.swift` calls the `loadSpec()` that `main.swift` defines; the export stands in
// for it with the same loader over its own argument, as W34's did.
func loadSpec() -> SceneSpecFile { try! SceneSpecFile.load(CommandLine.arguments[1]) }

func members(_ c: ComponentSpec) -> [ShapeSpec] {
  switch c {
  case .none: return []
  case .shape(let s): return [s]
  case .group(let items, _), .column(let items): return items
  case .stack(let base, let over): return [base, over]
  }
}

@main struct ExportPaths {
  static func main() throws {
    let file = CommandLine.arguments[1]
    let spec = try SceneSpecFile.load(file)
    let canvas = spec.canvas.cgSize
    let paths = spec.components.mapValues { suppliedShapePaths($0, canvas: canvas) }
    var checks: [String: [PositionCheck]] = [:]
    for (id, component) in spec.components {
      for (i, (shape, path)) in zip(members(component), paths[id]!).enumerated() {
        guard let p = shape.position else { continue }
        // The supplied path's own extent, in its local frame: what SwiftUI was handed, which
        // is the attestation X25 names — not the window server's raster.
        let local = CGRect(origin: .zero, size: shape.cgSize)
        let bounds = glassShape(shape).path(in: local).cgPath.boundingBoxOfPath
        let centre = [path.frameOrigin[0] + path.rect[2] / 2, path.frameOrigin[1] + path.rect[3] / 2]
        let b = [Double(bounds.minX), Double(bounds.minY), Double(bounds.width), Double(bounds.height)]
        checks[id, default: []].append(PositionCheck(
          member: i, kind: shape.kind, declaredPosition: p, declaredSize: shape.size,
          frameOrigin: path.frameOrigin, attestedCentre: centre, rect: path.rect, pathBounds: b,
          centreMatches: centre == p,
          sizeMatches: path.rect == [0, 0, shape.size[0], shape.size[1]],
          pathBoundsMatch: zip(b, path.rect).allSatisfy { abs($0 - $1) <= 1e-9 }))
      }
    }
    let flat = checks.values.flatMap { $0 }
    let allMatch = flat.allSatisfy { $0.centreMatches && $0.sizeMatches && $0.pathBoundsMatch }
    let out = Export(scenesFile: (file as NSString).lastPathComponent,
                     canvas: [spec.canvas.width, spec.canvas.height], components: paths,
                     positionChecks: checks, positionedShapes: flat.count, allMatch: allMatch)
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.sortedKeys, .prettyPrinted]
    FileHandle.standardOutput.write(try encoder.encode(out))
    FileHandle.standardOutput.write(Data("\n".utf8))
    if !allMatch {
      FileHandle.standardError.write(Data("export-paths: a positioned shape's attestation differs from its declaration\n".utf8))
      exit(1)
    }
  }
}
