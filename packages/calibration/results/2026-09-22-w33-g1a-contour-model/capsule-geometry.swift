// W33 G1a review closure (§5.171), 2026-09-22.
// Non-rendering SwiftUI path witness, adapted from the independent reviewer's capsule.swift.
// Run directly with swift; do not build or launch the capture harness.
import SwiftUI
import Foundation

let rect = CGRect(x: 0, y: 0, width: 120, height: 44)
var paths: [String: CGPath] = [:]
for (name, shape) in [("default", Capsule()), ("continuous", Capsule(style: .continuous)),
                      ("circular", Capsule(style: .circular))] {
    let path = shape.path(in: rect).cgPath
    paths[name] = path
    var elements: [[String: Any]] = []
    var previous = CGPoint.zero
    var straightStarts: [Double] = []
    path.applyWithBlock { pointer in
        let e = pointer.pointee
        let count: Int
        switch e.type {
        case .moveToPoint, .addLineToPoint: count = 1
        case .addQuadCurveToPoint: count = 2
        case .addCurveToPoint: count = 3
        default: count = 0
        }
        // Ignore degenerate lines and the circular path's floating-point y noise.
        if e.type == .addLineToPoint && abs(previous.y - e.points[0].y) < 1e-9
            && abs(previous.x - e.points[0].x) > 1e-9 {
            straightStarts.append(Double(min(previous.x, e.points[0].x)))
        }
        elements.append(["type": e.type.rawValue,
                         "points": (0..<count).map { [Double(e.points[$0].x),
                                                      Double(e.points[$0].y)] }])
        if count > 0 { previous = e.points[count - 1] }
    }
    let data = try! JSONSerialization.data(withJSONObject: ["name": name,
        "rect": [0, 0, 120, 44], "elements": elements,
        "straightSegmentStarts": straightStarts], options: [.sortedKeys])
    print(String(data: data, encoding: .utf8)!)
}
let defaultPath = paths["default"]!
print("default == continuous: \(defaultPath == paths["continuous"]!)")
print("default == circular: \(defaultPath == paths["circular"]!)")
precondition(defaultPath == paths["continuous"]!)
precondition(defaultPath != paths["circular"]!)
