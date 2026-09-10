// W27c G1 preflight proof (claims §5.128, §5.130). Not a reimplementation of the
// guard: this compiles directly against the real
// apps/reference-apple/Sources/SceneSpec.swift and calls the same pure method
// main.swift's `capture` and `dump-layers` preflights call —
// `SceneSpecFile.scenesUnsupportedForFreshCapture` — so a change to that method
// that stops refusing an inactive scene, or starts refusing an active one, fails
// here without opening a window or a display session. See
// 2026-09-10-w27c-g1-preflight-check.sh for how this is built and run.
import Foundation

enum Expectation: String { case refuse, pass }

@main
struct PreflightCheck {
  static func main() {
    let args = CommandLine.arguments
    guard args.count == 3, let expect = Expectation(rawValue: args[2]) else {
      FileHandle.standardError.write("usage: preflight-driver <scenes.json> <refuse|pass>\n".data(using: .utf8)!)
      exit(2)
    }
    do {
      let spec = try SceneSpecFile.load(args[1])
      let allIds = spec.scenes.map(\.id)
      let unsupported = spec.scenesUnsupportedForFreshCapture(allIds)
      switch expect {
      case .refuse:
        guard !unsupported.isEmpty else {
          print("FAIL: expected a refusal, got none — \(allIds.count) scene(s) all read as freshly capturable")
          exit(1)
        }
        print("PASS: refused on \(unsupported.count) of \(allIds.count) scene(s): " +
              unsupported.joined(separator: ", "))
      case .pass:
        guard unsupported.isEmpty else {
          print("FAIL: expected no refusal, got \(unsupported.count) of \(allIds.count): " +
                unsupported.joined(separator: ", "))
          exit(1)
        }
        print("PASS: no refusal — \(allIds.count) scene(s) all freshly capturable")
      }
    } catch {
      print("FAIL: spec failed to load or validate: \(error.localizedDescription)")
      exit(1)
    }
  }
}
