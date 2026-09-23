import Foundation
import SwiftUI

struct SuppliedPathElement: Codable, Equatable {
  let type: Int
  let points: [[Double]]
}

struct SuppliedShapePath: Codable {
  let kind: String
  let frameOrigin: [Double]
  let rect: [Double]
  let opaque: Bool
  let elements: [SuppliedPathElement]
}

/// Export the path handed to the fill/material, not a fitted raster contour.
/// Coordinates are CSS points, image-down, relative to each surface's frame.
func suppliedShapePaths(_ component: ComponentSpec, canvas: CGSize) -> [SuppliedShapePath] {
  func entry(_ s: ShapeSpec, origin: CGPoint? = nil) -> SuppliedShapePath {
    let rect = CGRect(origin: .zero, size: s.cgSize)
    var elements: [SuppliedPathElement] = []
    glassShape(s).path(in: rect).cgPath.applyWithBlock { pointer in
      let e = pointer.pointee
      let count: Int
      switch e.type {
      case .moveToPoint, .addLineToPoint: count = 1
      case .addQuadCurveToPoint: count = 2
      case .addCurveToPoint: count = 3
      case .closeSubpath: count = 0
      @unknown default: preconditionFailure("unknown CGPath element")
      }
      elements.append(.init(type: Int(e.type.rawValue), points: (0..<count).map {
        [Double(e.points[$0].x), Double(e.points[$0].y)]
      }))
    }
    let o = origin ?? CGPoint(x: (canvas.width - s.cgSize.width) / 2 + s.cgOffset.width,
                               y: (canvas.height - s.cgSize.height) / 2 + s.cgOffset.height)
    return .init(kind: s.kind, frameOrigin: [Double(o.x), Double(o.y)],
                 rect: [0, 0, s.size[0], s.size[1]], opaque: s.opaque == true, elements: elements)
  }
  switch component {
  case .none: return []
  case .shape(let s): return [entry(s)]
  case .stack(let base, let over): return [entry(base), entry(over)]
  case .group(let items, let spacing):
    let width = items.reduce(0) { $0 + $1.cgSize.width } + Double(items.count - 1) * spacing
    var left = (canvas.width - width) / 2
    return items.map { s in
      defer { left += s.cgSize.width + spacing }
      return entry(s, origin: CGPoint(x: left, y: (canvas.height - s.cgSize.height) / 2))
    }
  }
}
