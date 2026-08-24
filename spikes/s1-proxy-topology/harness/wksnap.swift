// Renders a URL with the system WKWebView (real WebKit.framework, real Core
// Animation compositing) and writes a PNG. Playwright's WebKit build no-ops
// backdrop-filter in its screenshot path, so this is the spike's only route to
// trustworthy WebKit pixels on this machine.
//
//   swiftc -O -o wksnap wksnap.swift
//   ./wksnap <url> <width> <height> <out.png> [delayMs] [dpr]
//
// This is a WKWebView, not Safari: same WebKit engine and compositor, without
// Safari's own chrome/feature layer. Findings from it are flagged accordingly.

import Cocoa
import WebKit

let args = CommandLine.arguments
guard args.count >= 5 else {
  FileHandle.standardError.write("usage: wksnap <url> <w> <h> <out.png> [delayMs] [dpr]\n".data(using: .utf8)!)
  exit(2)
}
let urlStr = args[1]
let W = Double(args[2])!
let H = Double(args[3])!
let out = args[4]
let delayMs = args.count > 5 ? Int(args[5])! : 700
let dpr = args.count > 6 ? Double(args[6])! : 1.0

final class Snapper: NSObject, WKNavigationDelegate {
  let web: WKWebView
  let win: NSWindow
  override init() {
    let cfg = WKWebViewConfiguration()
    cfg.preferences.setValue(true, forKey: "developerExtrasEnabled")
    let frame = NSRect(x: 0, y: 0, width: W, height: H)
    web = WKWebView(frame: frame, configuration: cfg)
    web.setValue(false, forKey: "drawsBackground")
    // An off-screen but ordered-front window: the layer tree is live, so
    // takeSnapshot goes through the real compositor.
    win = NSWindow(contentRect: frame,
                   styleMask: [.borderless],
                   backing: .buffered,
                   defer: false)
    win.setFrameOrigin(NSPoint(x: -20000, y: -20000))
    win.contentView = web
    win.orderFrontRegardless()
    super.init()
    web.navigationDelegate = self
  }

  func load(_ s: String) {
    guard let u = URL(string: s) else { exit(3) }
    if u.isFileURL {
      let dir = u.deletingLastPathComponent()
      web.loadFileURL(u, allowingReadAccessTo: dir.deletingLastPathComponent())
    } else {
      web.load(URLRequest(url: u))
    }
  }

  func webView(_ w: WKWebView, didFinish nav: WKNavigation!) {
    DispatchQueue.main.asyncAfter(deadline: .now() + .milliseconds(delayMs)) { self.snap() }
  }

  func webView(_ w: WKWebView, didFail nav: WKNavigation!, withError e: Error) {
    FileHandle.standardError.write("load failed: \(e)\n".data(using: .utf8)!)
    exit(4)
  }

  func snap() {
    let cfg = WKSnapshotConfiguration()
    cfg.rect = NSRect(x: 0, y: 0, width: W, height: H)
    cfg.snapshotWidth = NSNumber(value: W * dpr)
    cfg.afterScreenUpdates = true
    web.takeSnapshot(with: cfg) { img, err in
      guard let img = img, err == nil else {
        FileHandle.standardError.write("snapshot failed: \(String(describing: err))\n".data(using: .utf8)!)
        exit(5)
      }
      guard let tiff = img.tiffRepresentation,
            let rep = NSBitmapImageRep(data: tiff),
            let png = rep.representation(using: .png, properties: [:]) else { exit(6) }
      try? png.write(to: URL(fileURLWithPath: out))
      exit(0)
    }
  }
}

let app = NSApplication.shared
app.setActivationPolicy(.accessory)
let s = Snapper()
s.load(urlStr)
DispatchQueue.main.asyncAfter(deadline: .now() + 30) {
  FileHandle.standardError.write("timeout\n".data(using: .utf8)!)
  exit(7)
}
app.run()
