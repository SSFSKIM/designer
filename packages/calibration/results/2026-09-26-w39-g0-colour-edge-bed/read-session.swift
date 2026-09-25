// W39 session reader (c9a §5.184, charter clause 5), derived from W34 G0's
// read-session.swift. A non-GUI read of HID idle, the frontmost application, the
// screen lock and, new for W39, the on-screen window OWNERS. Compile it outside
// the repository (the README gives the command); it needs no Screen Recording
// grant and activates nothing.
//
// Why the window owners: a refusal rehearsal launches an UNGRANTED bundle into a
// real capture, and macOS may answer the first ScreenCaptureKit call from a new
// identifier with a visible permission prompt. The sitting reads the owners
// before and after the launch and names any owner that appeared as a pending
// prompt, rather than guessing which system process draws the prompt this
// release. Owner names and layers are readable without the grant; window titles
// are not, and none are read.
import AppKit
import Foundation
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
if let windows = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements],
                                            kCGNullWindowID) as? [[String: Any]] {
  var owners = Set<String>()
  for w in windows {
    let owner = w[kCGWindowOwnerName as String] as? String ?? "unknown"
    let layer = (w[kCGWindowLayer as String] as? NSNumber)?.intValue ?? 0
    owners.insert("\(owner)|\(layer)")
  }
  record["windowOwners"] = owners.sorted()
} else {
  record["windowOwners"] = NSNull()
}
print(String(data: try! JSONSerialization.data(withJSONObject: record, options: [.sortedKeys]),
             encoding: .utf8)!)
