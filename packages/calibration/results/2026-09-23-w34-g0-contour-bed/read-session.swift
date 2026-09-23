import Foundation
import AppKit
import IOKit
let service = IOServiceGetMatchingService(kIOMainPortDefault, IOServiceMatching("IOHIDSystem"))
var properties: Unmanaged<CFMutableDictionary>?
var record: [String: Any] = [:]
if service != 0 {
  if IORegistryEntryCreateCFProperties(service, &properties, kCFAllocatorDefault, 0) == KERN_SUCCESS,
     let dict = properties?.takeRetainedValue() as? [String: Any],
     let idle = dict["HIDIdleTime"] as? NSNumber { record["idleSeconds"] = idle.doubleValue / 1e9 }
  IOObjectRelease(service)
}
if let app = NSWorkspace.shared.frontmostApplication {
  record["frontmostIdentifier"] = app.bundleIdentifier ?? "unknown"
  record["frontmostPid"] = app.processIdentifier
}
if let session = CGSessionCopyCurrentDictionary() as? [String: Any] {
  record["screenLocked"] = session["CGSSessionScreenIsLocked"] ?? false
} else {
  record["screenLocked"] = NSNull()
}
print(String(data: try! JSONSerialization.data(withJSONObject: record, options: [.sortedKeys]), encoding: .utf8)!)
