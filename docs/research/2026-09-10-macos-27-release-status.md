# macOS 27 reference watch

**As of 2026-09-10.** Primary Apple sources are used unless a row says **secondary**.
Apple documentation pages without publication metadata are dated here by access date.

| Date | Version / build | Status relevant to the reference | Evidence |
|---|---|---|---|
| 2026-05-11 | macOS Tahoe 26.5 | Current project's public baseline | [Apple security-release index, published 2026-09-08](https://support.apple.com/en-us/100100) |
| 2026-06-08 | macOS 27 beta 1, 26A5353q | Golden Gate generation announced; developer seed | [Apple Newsroom, 2026-06-08](https://www.apple.com/newsroom/2026/06/apple-unveils-next-generation-of-apple-intelligence-siri-ai-and-more/); [Apple Developer Releases, 2026-06-08](https://developer.apple.com/news/releases/?id=06082026d) |
| 2026-08-17 | macOS Tahoe 26.6.2, 25G83 | **Latest public macOS 26.x** | [Apple Developer Releases, 2026-08-17](https://developer.apple.com/news/releases/); [Apple security note, published 2026-08-20](https://support.apple.com/en-us/148281) |
| 2026-09-09 | macOS Tahoe 26.7 RC 4, 25G229 | Not public; beta channels only | **Secondary:** [9to5Mac, 2026-09-09](https://9to5mac.com/2026/09/09/apple-rolls-out-fourth-developer-and-public-rcs-for-macos-tahoe-26-7-and-macos-sequoia-15-8/) |
| 2026-09-09 | **macOS 27.0 RC, 26A428** | **Current macOS 27 build; not GA** | [Apple Developer Releases, 2026-09-09](https://developer.apple.com/news/releases/) |
| 2026-09-14 | macOS 27 **Golden Gate** | Apple-scheduled public availability | [Apple macOS page, undated, accessed 2026-09-10](https://www.apple.com/os/macos/) |
## 1. Ship status

**No: macOS 27 has not shipped publicly as of 2026-09-10.** Apple's live page names it
**macOS 27 Golden Gate** and says it is “available starting 9.14”; Apple Developer lists only the
September 9 RC, build **26A428** ([Apple macOS page, accessed 2026-09-10](https://www.apple.com/os/macos/);
[Apple Developer Releases, 2026-09-09](https://developer.apple.com/news/releases/)). This official
build supersedes secondary reports that inserted an extra `54` and called it `26A5428`.
Recheck the build after GA; an RC is a candidate, not proof of the final public build.
## 2. Liquid Glass in the macOS 27 notes
### Material and visual behavior

- Apple says Liquid Glass now has “more uniform refraction and improved contrast,” alongside
  uniform toolbars, edge-to-edge sidebars, updated window shapes, and updated menu-bar icons
  ([Apple macOS page, accessed 2026-09-10](https://www.apple.com/os/macos/)).
- The developer explanation is more specific: Apple tuned the material to “more effectively diffuse
  complex content behind it” and added a **darkened edge** plus **brighter specular highlights** for
  depth and separation. Apps already using Liquid Glass receive those changes on the 27 OS “without
  even needing to recompile” ([Apple WWDC26 Platforms State of the Union, 2026-06-08](https://developer.apple.com/videos/play/wwdc2026/102/)).
- The same session says macOS windows get a common tighter corner radius; sidebars expand to the
  edges; and a uniform top toolbar preserves legibility as content scrolls underneath
  ([Apple WWDC26 Platforms State of the Union, 2026-06-08](https://developer.apple.com/videos/play/wwdc2026/102/)).
### Appearance slider

- Apple's exact range is **“ultraclear to fully tinted”** (Newsroom spells the first endpoint
  “ultra-clear”). Apple calls it only a “new slider in Settings”; it gives no numeric values or named
  stops ([Apple macOS page, accessed 2026-09-10](https://www.apple.com/os/macos/);
  [Apple Newsroom, 2026-06-08](https://www.apple.com/newsroom/2026/06/apple-unveils-next-generation-of-apple-intelligence-siri-ai-and-more/)).
- Apple has not yet published a macOS 27 User Guide page that establishes the control's exact label
  or path. Beta observers place **Liquid Glass** at **System Settings → Appearance**, with the slider
  centered by default, left = maximum transparency, and right = frosted/fully tinted. Treat those
  UI details as **secondary beta observations**, not final Apple documentation
  ([heise, 2026-06-12](https://www.heise.de/en/news/Liquid-Glass-New-slider-aims-to-calm-tempers-11330368.html);
  [iDownloadBlog, 2026-06-18](https://www.idownloadblog.com/2026/06/18/adjust-liquid-glass-ios-macos/)).
- For comparison, Apple's still-current Tahoe 26 guide documents **System Settings → Appearance →
  Liquid Glass** as two choices, **Clear** or **Tinted**; the `/27/` URL still serves 26 content
  ([Apple Mac User Guide, undated, accessed 2026-09-10](https://support.apple.com/guide/mac-help/change-appearance-settings-mchlp1225/27/mac/27)).
### Consumer and developer release notes

- No Apple Support “What's new in the updates for macOS 27” article was available on 2026-09-10.
  The official consumer text is therefore the June Newsroom release and live macOS page above.
  **Secondary:** 9to5Mac says it reproduces Apple's RC consumer notes unedited; their design section
  repeats improved readability, the ultraclear-to-fully-tinted slider, uniform toolbars,
  edge-to-edge sidebars, and more detailed icons
  ([9to5Mac, 2026-09-09](https://9to5mac.com/2026/09/09/macos-27-golden-gate-here-are-apples-full-release-notes/)).
- Apple's mutable RC developer notes do **not** name `glassEffect`, `Glass`,
  `GlassEffectContainer`, or `NSGlassEffectView`. Their only directly related fixes are an incorrect
  `NSSegmentedCell` position under Liquid Glass, missing hover state for SwiftUI `.glass` and
  `.glassProminent` buttons outside toolbars, and an `NSScrollView` scroll-edge effect appearing
  with no visible scrollers. Apps linked on 27 also let `NSTitlebarAccessoryViewController` draw
  outside its bounds for shadows and interactive glass effects
  ([Apple macOS 27 RC notes, undated, inspected 2026-09-10](https://developer.apple.com/documentation/macos-release-notes/macos-27-release-notes)).
- The one new glass symbol is **`NSGlassEffectView.effectIsInteractive`** (macOS 27.0), which adds a
  visual response to interaction. The SwiftUI `glassEffect`, `Glass`, and `GlassEffectContainer`
  documentation still exposes the 26-era surface with no 27 member
  ([Apple API docs, undated, accessed 2026-09-10: `effectIsInteractive`](https://developer.apple.com/documentation/appkit/nsglasseffectview/effectisinteractive),
  [`Glass`](https://developer.apple.com/documentation/swiftui/glass),
  [`glassEffect`](https://developer.apple.com/documentation/swiftui/view/glasseffect(_:in:)),
  [`GlassEffectContainer`](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)).
- Existing scroll-edge APIs remain the customization point, but behavior changes: on 27 the
  automatic `NSScrollEdgeEffectStyle` resolves to a **hard-edge** effect behind free-floating text
  such as a title-bar window title ([Apple “Modernize your AppKit app,” WWDC26, June 2026](https://developer.apple.com/videos/play/wwdc2026/289/)).
## 3. Did the 26.x reference move after 26.5?

**No documented material change.** Apple's 26.6/26.6.1/26.6.2 consumer history says bug/security
fixes (26.6 also prepares Spotlight's index for macOS 27), and its complete 26.6 developer notes
contain no Liquid Glass, glass, appearance, transparency, or tint item
([Apple Tahoe update history, published 2026-08-17](https://support.apple.com/en-us/122868);
[Apple macOS 26.6 developer notes, undated, inspected 2026-09-10](https://developer.apple.com/documentation/macos-release-notes/macos-26_6-release-notes)).
The latest public point release is 26.6.2; 26.7 is only RC. This is strong release-note evidence,
not proof that private rendering constants stayed byte-for-byte identical. For calibration-grade
certainty, run one controlled 26.5-vs-26.6.2 pixel comparison rather than silently relabeling fixtures.
## 4. Capture and accessibility implications

- **ScreenCaptureKit:** no macOS 27 RC note documents a still/stream pixel-path change, and Apple's
  ScreenCaptureKit update index has no 2025 or 2026 section. The only clearly new macOS 27 capture
  class is `SCRecordingEditor`, a system-owned preview UI for a completed recording—not a new
  acquisition path ([Apple ScreenCaptureKit updates and API docs, undated, inspected 2026-09-10](https://developer.apple.com/documentation/updates/screencapturekit);
  [`SCRecordingEditor`](https://developer.apple.com/documentation/screencapturekit/screcordingeditor)).
- **Screen Recording consent:** the RC notes announce no permission-flow change. A separate beta
  hardening may affect automation that edits `TCC.db`: an independent researcher found the user TCC
  database moved into a ProtectedSystem container, preventing direct modification even with Full
  Disk Access. This is **secondary beta research**, not an Apple capture guarantee
  ([Wojciech Reguła, published 2026-07-16, updated 2026-07-19](https://wojciechregula.blog/post/golden-gate-appdata-protection/)).
- **Reduce Transparency / Increase Contrast:** Apple says Liquid Glass continues adapting to both,
  and macOS 27 newly supports the **Show Borders** environment value
  ([Apple WWDC26 Platforms State of the Union, 2026-06-08](https://developer.apple.com/videos/play/wwdc2026/102/)).
  A quoted framework-engineer statement says Show Borders was decoupled from Increase Contrast for
  new-design apps, so capture the three settings independently; this statement is **secondary-carried**
  ([Michael Tsai update quoting Jeff Nadeau, 2026-06-11](https://mjtsai.com/blog/2026/06/09/macos-golden-gate-27-announced/)).
  Apple's current accessibility guide still serves Tahoe 26, contains no Show Borders entry, and has
  no update date ([Apple Mac User Guide, accessed 2026-09-10](https://support.apple.com/guide/mac-help/change-display-settings-for-accessibility-unac089/mac)).
## Reference decision

Keep **26.5** as the existing frozen profile through 2026-09-13. The reference moves when a clean
machine installs the **public macOS 27 Golden Gate build on or after 2026-09-14**, and that must be a
new profile: the diffusion, edge darkening, specular intensity, refraction/contrast, and geometry all
change automatically, while the user-selected Liquid Glass slider position becomes a required fixture
axis. Record the exact GA build plus slider position, Reduce Transparency, Increase Contrast, Show
Borders, display/HDR state, and capture color settings; do not mix 27 captures into the 26.5 profile.
