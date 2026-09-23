import Foundation
import SwiftUI
func loadSpec() -> SceneSpecFile { try! SceneSpecFile.load(CommandLine.arguments[1]) }
@main struct Export {
  static func main() throws {
    let spec=loadSpec()
    let paths=spec.components.mapValues { suppliedShapePaths($0, canvas: spec.canvas.cgSize) }
    let encoder=JSONEncoder();encoder.outputFormatting=[.sortedKeys,.prettyPrinted]
    FileHandle.standardOutput.write(try encoder.encode(paths))
  }
}
