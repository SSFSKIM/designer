# Glass as the surface: Apple's spatial and system-surface precedents

> Research report, 2026-09-27, for a second material register in the materialist skill.
> Companion to `2026-09-10-liquid-glass-design-language.md` and
> `2026-09-26-liquid-glass-aesthetic-prior-art.md`; those cover the controls-over-content register.
> This report records precedent, not instructions for the skill. Apple sources are **primary**;
> independent criticism is marked **secondary**. Quotes were retrieved during this research.
> HIG pages whose HTML returned only a title were read through Apple's own documentation JSON,
> linked beside the public page. No live-app visual or contrast testing was performed.

## 1. The important distinction: visionOS glass is not simply Liquid Glass enlarged

**The strongest Apple precedent for glass as the primary surface is the visionOS window.** It is
explicitly a canvas for an app's content and UI, not just a housing for its navigation. Apple's
visionOS guidance therefore cannot be reduced to the iPhone rule against glass in the content
layer. Equally, it does not establish that every material Apple calls glass is interchangeable.

- **Primary — [HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
  ([Apple JSON](https://developer.apple.com/tutorials/data/design/human-interface-guidelines/materials.json)):**
  “In visionOS, windows generally use an unmodifiable system-defined material called *glass* that
  helps people stay grounded by letting light, the current Environment, virtual content, and
  objects in people's surroundings show through.”
- The same page's separate **Liquid Glass** section says “Don't use Liquid Glass in the content
  layer.” Its visionOS section nevertheless recommends glass windows and describes materials
  for sidebars and grouped tables. These are platform-specific prescriptions, not a universal
  prohibition on readable content residing on a translucent surface.
- **Primary — [Apple's 2025 design announcement](https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/):**
  Liquid Glass is “Inspired by the depth and dimensionality of visionOS.” The platforms named
  for the new cross-platform design are iOS, iPadOS, macOS, watchOS and tvOS; visionOS is the
  inspiration, not another name in that list.
- **Secondary — [Devon Dundee, MacStories, visionOS 26 review](https://www.macstories.net/stories/visionos-26-the-macstories-review/7/):**
  visionOS “didn't get the Liquid Glass treatment aside from some updated icons on the Home View”;
  “window chrome continues to employ a frosted glass look.” He notes Liquid Glass in compatible
  iPad apps and calls the mixed treatments confusing. This is a reviewer observation, not an API
  specification, but it is a useful guard against treating the two materials as identical.

There are also three different meanings of **clear** in the evidence: the developer's
`Glass.clear` variant, the user's Clear/Tinted appearance preference, and the clear icon/widget
appearance. None can safely stand in for the other two. Sections 4–5 keep them separate.

## 2. visionOS: the whole window as a glass canvas

### 2.1 Why it is glass, and what is behind it

**Primary — [WWDC23 10076, Design for spatial user interfaces](https://developer.apple.com/videos/play/wwdc2023/10076/):**

> “And its unique properties allow light from people's surroundings and virtual content to show
> through. In addition, specular highlights and shadows reinforce its scale and position in your
> space. And it works as a canvas for your contained UI, making it feel lighter and adding a sense
> of physicality to it. This lightweight material also gives people a sense of what might be behind
> a window, like other apps or people.”

> “Avoid using solid colors on windows. Too many opaque windows can feel constricting and make the
> interface feel heavy.”

**Primary — [WWDC23 10072, Principles of spatial design](https://developer.apple.com/videos/play/wwdc2023/10072/):**

> “The glass material provides contrast with the world, gives people more awareness of their
> surroundings, and adapts to different lighting conditions.”

The backdrop is **not necessarily controlled or quiet**. It can be a daylight room, an airplane,
nighttime surroundings, other apps or an Environment. Apple compensates through a system material
that transforms that information, rather than expecting raw transparency to remain readable.

**Primary — HIG Materials, visionOS:**

> “Glass is an adaptive material that limits the range of background color information so a window
> can continue to provide contrast for app content while becoming brighter or darker depending on
> people's physical surroundings and other virtual content.”

> “visionOS doesn't have a distinct Dark Mode setting. Instead, glass automatically adapts to the
> luminance of the objects and colors behind it.”

**Primary — [HIG Windows](https://developer.apple.com/design/human-interface-guidelines/windows)
([Apple JSON](https://developer.apple.com/tutorials/data/design/human-interface-guidelines/windows.json)):**

> “The default window style consists of an upright plane that uses an unmodifiable background
> material called *glass* and includes a close button, window bar, and resize controls that let
> people close, move, and resize the window.”

> “Retain the window's glass background.”

> “Removing the glass material tends to cause UI elements and text to become less legible and to
> no longer appear related to each other; using an opaque background obscures people's surroundings
> and can make a window feel constricting and heavy.”

Thus Apple's alternative to an opaque window is **a substantial, adaptive backing**, not text and
buttons floating naked in passthrough. A plain window style exists, but it is not the default
recommendation for a conventional interface.

### 2.2 Content really does sit on it: collections, text, imagery, sections

WWDC23 10076 walks through Music, beginning with a glass window, then its sidebar, buttons and text.
It also describes image-and-label collections and lists on that interface:

> “Here, we have some images with text below them. Each lock-up is a single interactive element.”

> “For example, if you're creating a list or a menu, you need to account for a small amount of
> padding in between each item to avoid having the hover effect overlap. Four points is recommended.”

This is broader than short control labels. No one-line limit on content, or blanket ban on lists
and grouped tables on the window, appears in these sources. The HIG explicitly names a grouped
table as a use for a separating material. That does **not** establish that unlimited prose density
or every possible document should be translucent; the sources provide no such density threshold.

**Primary — [WWDC24 10086, Design great visionOS apps](https://developer.apple.com/videos/play/wwdc2024/10086/):**

> “The content and UI of your app should be contained in a window. Controls like Tab bars and
> Toolbars can live outside the window, but they are still anchored to the view.”

> “Spatial doesn't mean buttons and UI should be arbitrarily floating in peoples field of view.”

Apple's featured Red Bull TV example is particularly concrete. Its mobile/TV dark-blue brand
background gave way to imagery plus glass on Vision Pro:

> “But when you scroll the main view, the rest of the window uses the Glass background, opposed to
> a solid background color. Find ways like this to incorporate your branding without compromising
> comfort or usability.”

> “It can be visually distracting and uncomfortable to use solid backgrounds on windows. They don't
> adapt to our environments lighting and they block our view of the world.”

The featured developer describes using the dark-blue brand color briefly while images load. Apple
presents imagery and small branding moments, rather than a saturated full-window backing, as the
way this particular app keeps its identity. The session includes the developer's own testimony;
it is an Apple-selected example, not a claim that Apple designed Red Bull TV.

### 2.3 Nested elements: materials with roles, not repeated glass panes

**Primary — WWDC23 10076:**

> “First, we start with a glass window. If you want to separate sections of your app, like a
> sidebar, use a darker material. Or a lighter material to bring attention to interactive elements,
> like buttons. Or you might even consider using darker materials to increase contrast for standard
> components, like input fields.”

> “Try to not stack lighter materials on top of each other, as it impacts legibility and reduces
> contrast.”

**Primary — HIG Materials, visionOS:**

- “The `thin` material brings attention to interactive elements like buttons and selected items.”
- “The `regular` material can help you visually separate sections of your app, like a sidebar or a
  grouped table view.”
- “The `thick` material lets you create a dark element that remains visually distinct when it's on
  top of an area that uses a `regular` background.”

These are standard material roles *inside* a glass window. Their `regular` is not a statement that
the window is implemented with the cross-platform `Glass.regular` API. The spatial rule is more
specific than “never layer anything translucent”: avoid accumulating light layers that wash out
contrast; separate content with darker treatments and reserve light treatments for interaction.
The newer Liquid Glass advice independently says to use fills, transparency and vibrancy above
its material rather than put another Liquid Glass layer on it (WWDC25 219).

### 2.4 Vibrancy: hierarchy and legibility, not ordinary low-opacity ink

**Primary — WWDC23 10076:**

> “Vibrancy brightens foreground content that displays on top of a material and works by pulling
> light and color forward from what's behind it. On this platform, since the background can be
> constantly changing, vibrancy updates in real time to make sure your text is always legible.”

> “Use vibrancy to indicate hierarchy for text, symbols, and fills. There are three modes: primary,
> secondary, and tertiary. Use primary for standard text. Or use secondary for description text,
> footnotes, and subtitles.”

**Primary — HIG Materials** names the corresponding semantic values:

- “Use `label` for standard text.”
- “Use `secondaryLabel` for descriptive text like footnotes and subtitles.”
- “Use `tertiaryLabel` for inactive elements, and only when text doesn't need high legibility.”

Apple's “always legible” is the session's intent, not a measured guarantee for every backdrop or
custom implementation. System components receive the treatment by default. This source gives
three spatial vibrancy levels; it does not validate any web runtime's particular label algorithm.

### 2.5 Typography and dark content

**Primary — WWDC23 10076:**

> “To improve the contrast of text against vibrant materials, font weight has been modified to be
> slightly heavier. For example, on iOS, we use regular weight for the body text style. On this
> platform, we use medium. And for titles, instead of semibold, we use bold, keeping text clear all
> the time. Consequently, the tracking has been slightly increased to help with legibility.”

> “Even though windows can scale up to incredible large sizes, custom smaller or lightweight fonts
> can still be difficult to read.”

**Primary — [HIG Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
([Apple JSON](https://developer.apple.com/tutorials/data/design/human-interface-guidelines/typography.json)):**

> “By default, the system displays text in white, because this color tends to provide a strong
> contrast with the default system background material, making text easier to read. If you want
> to use a different text color, be sure to test it in a variety of contexts.”

> “Use a text style that makes the text look good at full scale, then test it for legibility at
> different scales.”

The HIG prefers little or no visual depth for text people must read and understand. For text without
a background, it suggests bold rather than a fabricated shadow: the space may contain no surface
on which to cast one, and the appropriate size and density cannot be predicted.

**Dark is a supported contrast device, not the default text treatment.** The darker materials in
§2.3 support separation and input fields. WWDC23 10076 gives a precise dark-label exception:

> “On this platform, we always use black labels on a white background to show buttons are selected.”

It also says to avoid white button backgrounds unless selected. The sources do not prohibit dark
photographs or dark media on the window, but they do not recommend arbitrary black body text
directly on adaptive glass. There is no distinct spatial Dark Mode to use as a substitute for
checking the actual backdrop.

### 2.6 Color and light: the environment participates, foreground meaning remains readable

**Primary — [HIG Color](https://developer.apple.com/design/human-interface-guidelines/color)
([Apple JSON](https://developer.apple.com/tutorials/data/design/human-interface-guidelines/color.json)):**

> “Use color sparingly, especially on glass.”

> “Because the colors in these physical and virtual objects are visible through the glass, they
> can affect the legibility of colorful app content in the window.”

> “Prefer using color in bold text and large areas. Color in lightweight text or small areas can
> make them harder to see and understand.”

**Primary — WWDC23 10076:**

> “Most of the time, consider using white text or symbols so they are always clearly visible. If
> you need to use color, use it in a background layer or an entire button so people can see it.”

System colors are preferred because they are calibrated to adapt hue and contrast on glass. The
exact prohibition “avoid saturated backgrounds” was **not found** in these fetched passages.
What is documented is sparing color, avoiding opaque window fills, and using bold/large colored
content rather than fragile colored type. That is narrower and more useful than inventing a ban
on saturated photographs or every saturated UI element.

“Glass takes light from the environment” has direct support in §2.1. **Light spill is a different
phenomenon**: WWDC23 10072 says, “Any object that appears to emit light should shine color onto
nearby objects.” Its example is a movie screen casting light onto floor and ceiling; most other
objects, including windows, should cast shadows. Environmental response does not imply that every
glass panel is an emissive lamp.

### 2.7 Ornaments and restraint in large surfaces

**Primary — [HIG Ornaments](https://developer.apple.com/design/human-interface-guidelines/ornaments)
([Apple JSON](https://developer.apple.com/tutorials/data/design/human-interface-guidelines/ornaments.json)):**

> “In visionOS, an ornament presents controls and information related to a window, without crowding
> or obscuring the window's contents.”

> “An ornament floats in a plane that's parallel to its associated window and slightly in front
> of it along the z-axis.”

> “By default, an ornament's background is glass, so if you place a button directly on the
> background, it may not need a visible border.”

Ornaments stay attached when the window moves and remain unchanged when its content scrolls.
Music's Now Playing controls are the named example. Apple recommends consistent visibility, with
hiding while viewing photos or video as a reasonable exception; width no greater than the window;
and constraining their number when they add weight or distraction. Content and controls can thus
both have glass backings **without becoming an arbitrary stack of glass cards**: the main canvas
and its spatially attached controls have different jobs and positions.

**Primary — WWDC23 10072:** “Windows aren't bound by a screen, so they should remain smaller when
possible to avoid blocking too much of people's view.” The session prefers a single window where
possible. HIG Windows similarly says to minimize empty areas in the initial window. Glass is not
permission to make every surface enormous.

### 2.8 When the material is not enough

**Primary — [Apple Vision Pro: Adjust colors and contrast](https://support.apple.com/guide/apple-vision-pro/colors-and-contrast-tandd53c64c3/visionos):**

> “Some backgrounds appear transparent or blurred by default.”
>
> “You can make these transparent backgrounds opaque by giving them a solid color.”

Apple supplies Reduce Transparency, plus Increase Focus State, Reduce White Point and color
adjustments. An opaque accessibility result is therefore part of Apple's own spatial system,
not a forbidden violation of its preference for translucency.

For media, WWDC23 10072 supplies another escape from background competition:

> “When it's time to watch a movie, the video takes over the entire window and passthrough is
> darkened.”

> “Dimming is a simple way to create contrast between your content and people's surroundings
> without taking them out of their space.”

## 3. visionOS 26 and 27: glass carries information, but not always by the same optics

**Primary — [WWDC25 255, Design widgets for visionOS](https://developer.apple.com/videos/play/wwdc2025/255/)**
provides another explicit information-on-glass precedent, with an important difference from windows:

> “While Paper focuses on blending into the space, Glass takes a different approach -- one that
> emphasizes clarity and contrast, especially for information-rich widgets.”

> “The foreground elements are always shown in full color, unaffected by the ambient lighting,
> keeping key content sharp and legible throughout the day.”

Apple describes a system frame, app-defined backplate, dark shadow-like **UI Duplicate Layer**,
foreground **UI Layer**, and reflective **Coating Layer**:

> “The UI Layer is where key content like text, glyphs, and graphs live -- elements that need to
> remain bright, crisp, and highly legible.”

> “In this News widget, for example, editorial images sit in the background with a soft, print-like
> feel, while headlines stay in the foreground, always clear and easy to read.”

> “Paper dims with the room to stay visually integrated, while Glass keeps foreground elements
> bright and legible, even in low light.”

This is not evidence for applying environmental dimming to all foreground content. Apple explicitly
separates what responds to the room from what stays bright. Glass and Paper are alternative widget
treatments, and this glass has its own layered structure; it is not proof that every glass style
shares window vibrancy or `Glass.clear` behavior.

**Primary — [WWDC25 317, What's new in visionOS 26](https://developer.apple.com/videos/play/wwdc2025/317/):**
widgets “can snap to walls and tables, blending into your environment and remaining right where you
place them.” A proximity API lets them display “just the right amount of information”; the
`widgetTexture` API changes appearance “from glass to paper.” The transcript does not call the
window material Liquid Glass.

**Primary — [WWDC26 287, Build next-generation experiences with visionOS 27](https://developer.apple.com/videos/play/wwdc2026/287/)**
was checked. It discusses windows, volumes, wider Safari windows and immersion, but contains no
claim that spatial windows now adopt Liquid Glass. No primary-source visionOS 27 replacement of
the window-material model was found in this research; the session's absence of such a claim is
not proof that no other source exists.

## 4. Clear versus regular: what the permission actually covers

### 4.1 The conditions, freshly verified

**Primary — [WWDC25 219, Meet Liquid Glass](https://developer.apple.com/videos/play/wwdc2025/219/):**

> “Regular is the most versatile and the one you will be using the most.”

> “Clear, on the other hand, does not have adaptive behaviors. It is permanently more transparent,
> which allows the richness of the content underneath to come through and interact with the glass
> in beautiful ways.”

> “To provide enough legibility for symbols or labels, it needs a dimming layer to darken the
> underlying content. Without it, legibility gets noticeably worse.”

Its three conditions are explicit:

> “First, the element you're applying it to is over media-rich content. Second, your content layer
> won't be negatively affected by introducing a dimming layer. And lastly, the content sitting
> above it is bold and bright.”

The session permits localized dimming for small-footprint elements. It says the two variants
“should never be mixed,” but its broad claim that regular can work anywhere does not repeal the
same session's placement restrictions. Neither variant is a declaration that app content should
become a collection of translucent cards.

**Primary — HIG Materials** supplies the more contextual wording:

> “Use the regular variant when background content might create legibility issues, or when
> components have a significant amount of text, such as alerts, sidebars, or popovers.”

> “If the underlying content is bright, consider adding a dark dimming layer of 35% opacity.”

> “If the underlying content is sufficiently dark, or if you use standard media playback controls
> from AVKit that provide their own dimming layer, you don't need to apply a dimming layer.”

**The number needs precise attribution.** The HIG says **dark, 35%**. The
[SwiftUI `Glass.clear` documentation](https://developer.apple.com/documentation/swiftui/glass/clear)
([Apple JSON](https://developer.apple.com/tutorials/data/documentation/swiftui/glass/clear.json))
says “adding a dimming layer or other treatment beneath the glass,” then illustrates it with
`.background(.black.opacity(0.3))`: **black, 30%**. WWDC25 219 names no percentage. “Apple requires
35% black” would overstate all three: 35% is the HIG's conditional suggestion, not a universal
constant, and its wording is not “black.”

### 4.2 Where Apple uses it, and where attribution is not established

The HIG explicitly names **photos and videos as background categories** and **AVKit's media
playback controls** as already supplying dimming. This is primary evidence for the media use case.
It does not identify the internal variant of every control in Photos or a video player.

No fetched primary source explicitly assigned `.clear` to **Photos, Camera or Maps by app name**.
The [Meet with Apple 201 transcript](https://developer.apple.com/videos/play/meet-with-apple/201/)
says Maps has “custom Liquid Glass controls that float above the map content,” but does not name
the variant. Searches for Camera mostly returned developer questions attempting to reproduce its
picker, not Apple confirmations. Those questions are not evidence of Apple's implementation.

[WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/) does not discuss the clear variant
by name. It supplies a different reason for dimming a larger surface:

> “When a task interrupts the main flow, pair Liquid Glass with a dimming layer to help center
> attention, making the sheet feel like a clear, purposeful space.”

It says a sheet becomes more opaque as focus deepens. Dimming for **modality** and dimming for
**clear-glass contrast** are related protections, but not the same requirement.

### 4.3 User preferences are not developer variants

**Primary — [Apple's iOS 26 release notes, iOS 26.1](https://support.apple.com/en-us/123075):**

> “Liquid Glass setting gives you the option to choose between the default clear look or a new
> tinted look which increases opacity of the material in apps and notifications on the Lock Screen”

This confirms notifications as content-bearing material and opacity as a user-selectable
legibility measure. iOS 26.2 separately adds adjustment of Lock Screen time, “giving the Liquid
Glass material more or less opacity.” The appearance preference does not mean an app switches
its entire interface to the developer's nonadaptive `.clear` variant.

**Primary — [Apple's macOS 27 release notes](https://support.apple.com/en-us/127257):**

> “Updates to Liquid Glass improve readability”
>
> “a new slider lets you customize how it looks, from ultra-clear to fully tinted.”

The fetched page does not prescribe a position for particular content, give numerical values for
intermediate positions, or define how the endpoints change each optical parameter. No claim that
50% is Apple's recommended design position is supported here. The iOS 26 user-guide page was also
attempted, but its fetched body was truncated; the release notes, not that partial fetch, support
the quotations above.

## 5. Other Apple surfaces: which are evidence, and which are not

### 5.1 Control Center and Notification Center

**Primary — Apple's 2025 design announcement** explicitly includes “the Lock Screen, Home Screen,
notifications, Control Center, and more.” These are system experiences, not an app's conventional
content layer. Control Center is primarily a control surface; notifications also carry message
content. The iOS 26.1 opacity setting explicitly reaches Lock Screen notifications (§4.3).

The fetched announcement does not specify a per-component blur radius, vibrancy level or dimming
amount. Its inclusion of notifications does not prove that every Notification Center region on
every platform uses the same material. **No distinct primary-source technical account of macOS
Notification Center's glass composition was found.** It remains a named research limit, rather
than a guessed extension of the iPhone behavior.

### 5.2 Lock Screen: glass can be the glyph, not its background

**Primary — Apple's 2025 design announcement:**

> “the time is now crafted out of Liquid Glass and fluidly adapts to fit elegantly behind the subject”

Its caption describes the San Francisco numerals dynamically changing weight, width and height.
This is **large display information**, often over a user-chosen photograph, not long-form body text
on an invisible pane. Notifications are separate content-bearing backings; Lock Screen widgets
use their own rendering treatment. The distinction matters: a glass clock does not establish a
safe paragraph treatment.

**Primary — [HIG Widgets](https://developer.apple.com/design/human-interface-guidelines/widgets)
([Apple JSON](https://developer.apple.com/tutorials/data/design/human-interface-guidelines/widgets.json))**
places Lock Screen/StandBy contrast guidance in **vibrant rendering**, not the clear Home Screen
appearance. It calls for enough contrast for legibility and uses brighter gray/white for prominent
content and darker gray for secondary content. These are separate contexts in the documentation,
not a universal instruction to use one set of opacities everywhere.

### 5.3 Home Screen widgets and the clear icon look

**Primary — HIG Widgets:**

> “In a clear appearance, the system desaturates the widget and adds translucency, highlights, and
> the Liquid Glass material.”

> “In the accented rendering mode, the system removes the background and replaces it with a tinted
> color effect for a tinted appearance and a Liquid Glass background for a clear appearance.”

The system separates the widget's views into primary and accent groups and applies solid colors
to them. This is an unambiguous Apple precedent for **information content on a glass backing**,
not only navigation. It is also a system-constrained transformation rather than an unrestricted
full-color dashboard style.

> “Convey meaning without relying on specific colors to represent information.”

> “Consider reserving full-color images to represent media content, such as album art for a music
> app's widget, and use full-color images with smaller dimensions than the size of the widget.”

The page prefers system fonts and symbols, text at 11 points or larger, and nonrasterized text.
That 11-point figure is widget guidance, not a prescription for visionOS body text.

**Primary — [WWDC26 8012, Icon Composer for Beginners Group Lab](https://developer.apple.com/videos/play/wwdc2026/8012/), around 34:37:**
when asked about a clear icon failing at extreme slider settings, the panel says the clear-mode
icon glass “does not respond to the slider” and “does not behave like system glass. It stays
constant.” Apple explains that arbitrary icon artwork makes a consistent, legible experience
important, so it pinned that glass. This explicitly distinguishes the clear **icon look** from
the user's system-material appearance slider; it does not establish identical behavior for widgets.

### 5.4 Dynamic Island: a counterexample, not a glass-surface precedent

**Primary — [HIG Live Activities](https://developer.apple.com/design/human-interface-guidelines/live-activities)
([Apple JSON](https://developer.apple.com/tutorials/data/design/human-interface-guidelines/live-activities.json)):**

> “Live Activities in the Dynamic Island use a black opaque background. Consider using bold colors
> for text and objects to convey the personality and brand of your app.”

Its compact, minimal and expanded backgrounds are not app-customizable. A key line distinguishes
the Island against dark backgrounds. Liquid Glass cites its fluidity as lineage, but that is not
evidence its primary surface is transparent. Its explicit opaque backing is a useful boundary on
the analogy.

### 5.5 tvOS 26: media stays visible, focus can introduce glass

**Primary — HIG Materials, tvOS:**

> “In tvOS, Liquid Glass appears throughout navigation elements and system experiences such as Top
> Shelf and Control Center. Certain interface elements, like image views and buttons, adopt Liquid
> Glass when they gain focus.”

The same section says standard materials continue to “define structure in the content layer,”
including `ultraThin` for full-screen views requiring a light color scheme and thicker materials
for overlays. **A whole-screen standard-material surface is not automatically whole-screen Liquid
Glass.** The sources do not support conflating the two.

**Primary — [Apple's tvOS 26 announcement](https://www.apple.com/newsroom/2025/06/apple-tv-brings-a-beautiful-redesign-and-enhanced-home-entertainment-experience/):**
video remains prominent while “starting a sleep timer, adjusting audio, or setting a ‘Movie night’
scene in Control Center.” It also describes poster artwork incorporating Liquid Glass. This is
media-first, with task controls layered over a continuing video, not arbitrary prose on glass.
The announcement supplies no numerical dimming or contrast recipe.

**Primary — [HIG Focus and selection](https://developer.apple.com/design/human-interface-guidelines/focus-and-selection)
([Apple JSON](https://developer.apple.com/tutorials/data/design/human-interface-guidelines/focus-and-selection.json)):**
“A focused item visually stands out from the other onscreen content through elevation to the
foreground, illumination, and animation.” It asks designers to allow for the enlarged focused
state without crowding. This is general tvOS focus guidance; that page does not specify the
Liquid Glass focus shader or establish that transparency alone signals focus.

### 5.6 watchOS 26: glanceable content and full-screen modal material

**Primary — [Apple's watchOS 26 announcement](https://www.apple.com/newsroom/2025/06/watchos-26-delivers-more-personalized-ways-to-stay-active-and-connected/):**
“Smart Stack widgets, Smart Stack hints, notifications, Control Center, and in-app controls and
navigation” adopt the new design. The Photos face has “numerals made of Liquid Glass, allowing
users to see even more of their photo.” Hints are glass “gentle visual” prompts.

**Primary — HIG Materials, watchOS:**

> “Use materials to provide context in a full-screen modal view.”

> “Because full-screen modal views are common in watchOS, the contrast provided by material layers
> can help orient people in your app and distinguish controls and system elements from other
> content. Avoid removing or replacing material backgrounds for modal sheets when they're provided
> by default.”

This is genuine larger-surface material guidance, but the passage says **materials**, not that
every full-screen modal uses the clear Liquid Glass variant. The announcement provides no
component-specific contrast formula. The evidence supports short, glanceable information and
context-preserving system material, not a broad claim about dense watch text on clear glass.

### 5.7 CarPlay: bounded widgets and navigation controls, not an unrestricted glass canvas

**Primary — [WWDC25 216, Turbocharge your app for CarPlay](https://developer.apple.com/videos/play/wwdc2025/216/):**

> “With iOS 26, buttons in the CPMapTemplate automatically get a Liquid Glass appearance. Be sure
> to test the ways your button icons look with CarPlay Simulator.”

For widgets, the session says:

> “Great widgets on iPhone provide simple, glanceable information, and the same is true in CarPlay.”

> “It's also best to use system fonts and colors to make sure your text is legible in different
> contexts.”

CarPlay tailors widget margins and can remove the widget background. High-density text is named
as potentially unsuitable. These are primary-source constraints, but the transcript does not
establish that an entire CarPlay content window is glass or identify a clear-variant dimming law.

## 6. Failure literature: additions and limits, not another reception roundup

The two companion reports already quote Gruber's “see-through blandness,” NN/g's criticism of
iOS 26, the beta backlash, and the beta 3/beta 4 opacity changes. The additions here are the points
that bear specifically on sustained content on large translucent surfaces.

### 6.1 Spatially variable contrast: one average is not enough

**Secondary — [NN/g, Glassmorphism](https://www.nngroup.com/articles/glassmorphism/):**

> “your text might only have enough contrast over certain areas”

> “More background blur is better, especially with intricate backgrounds”

NN/g criticizes examples that “try too hard to keep background elements distinguishable.” It
recommends simple or single-color backgrounds where the designer controls them, stronger blur
where arbitrary photography/video can appear, and transparency/contrast accessibility options.
This usefully challenges the assumption that a glass surface needs a conspicuously busy backdrop
to be successful. For text, the optical demonstration competes with the task.

This article is expert guidance illustrated with examples, **not a reported controlled user study
of visionOS windows**. Its specific charge is local contrast variation and competing attention;
it does not provide an empirical maximum amount of prose that glass can carry.

### 6.2 The beta corrections were not a universal opacity switch

**Secondary — [MacRumors, beta 3 comparisons](https://www.macrumors.com/guide/ios-26-beta-3-liquid-glass-changes/):**
“Apple made navigation bars more opaque across many apps in iOS 26 beta 3,” but “Home Screen and
Control Center haven't changed much if at all.” Notifications were darker over some backgrounds,
not uniformly, and Maps was reported as more translucent.

**Secondary — [9to5Mac, beta 4 comparison](https://9to5mac.com/2025/07/22/ios-26-beta-4-adds-more-liquid-back-to-liquid-glass-design/):**
“in the beta 2 and beta 4 images, the tab bar reveals much more of the content underneath it.”
Its examples include App Store, Photos and Music tab bars. This supports a partial reversal in
particular UI, not a measured system-wide return to one earlier transparency value. Apple's later
Clear/Tinted control is documented independently in §4.3; the connection to backlash is historical
interpretation, not Apple's stated reason in those release notes.

### 6.3 visionOS criticism: a promising lead, not verified headset evidence

Search located [Kasper Borgbjerg's accessibility case study](https://medium.com/@kasperib/accessibility-case-study-of-visionoss-gui-263f966e6fa6),
which discusses weak contrast over light surroundings and community visionOS designs. Full fetch
returned **403**. It is not quoted here or treated as a measured failure of Apple's live adaptive
material: mockups, screenshots and headset observations would need to be separated first.
No strong, fully retrieved visionOS-era usability study isolating busy passthrough behind Apple's
native glass windows was found in this search. That gap must not be filled by attributing generic
glassmorphism mockup problems to the shipped spatial system.

Apple's own heavier type, adaptive range-limiting, dark separating materials and opaque
accessibility option are direct evidence that legibility needs active protection. They are not,
by themselves, evidence that those protections always succeed.

## 7. Web precedent: no qualifying product established

No well-verified web product meeting the requested bar — glass as the sustained primary interface
surface, not an effect demo, a card or floating chrome — was established in this search. Linear's
[A Linear spin on Liquid Glass](https://linear.app/now/linear-liquid-glass) surfaced, but the
implementation described is its **native iOS app**, not evidence about its web app. It is not
promoted here into a web precedent. Omitting an example is preferable to treating a Dribbble mockup
or a glassmorphism tutorial as a working product.

## 8. What Apple's own use of glass as a surface has in common

These are conditions supported by the sources above, not proposed rules for the skill. They are
not all identical across platforms; the shared point is the deliberate protection around the
material, rather than maximum transparency.

1. **There is a reason to preserve awareness of what is behind it.** Spatial windows keep people
   grounded in physical/virtual surroundings; TV overlays preserve a continuing video; the clock
   preserves a photograph (§§2.1, 5.2, 5.5). Apple does not require that every backdrop be busy or
   designer-controlled. Where it is uncontrolled, the system takes responsibility for adaptation.
2. **The glass is a legibility-bearing backing, not an absence of a surface.** visionOS limits the
   range of background information and warns that removing its backing disconnects elements and
   makes text less legible (§2.1). Translucency and contrast are designed together.
3. **Foreground information receives its own treatment.** Spatial text, symbols and fills use
   semantic vibrancy; spatial widget foregrounds instead remain full-color and unaffected by room
   lighting; clear Home Screen widgets get system-managed color groups (§§2.4, 3, 5.3). Raw ink
   inheriting all of the backdrop's variation is not the common model.
4. **Glass can carry real content, but its scope is bounded.** Apple demonstrates lists,
   image-and-text collections, grouped tables, widget headlines and graphs (§§2.2, 3). Windows
   contain an app's content; glanceable surfaces carry smaller information units. No source here
   provides a universal one-line limit or permission for arbitrary dense prose.
5. **Nested hierarchy does not come from repeating identical glass sheets.** Spatial sections
   darken, interactive elements lighten, and light-on-light stacks are discouraged; ornaments are
   attached, separately positioned and limited in number (§§2.3, 2.7). A containing glass canvas
   is compatible with internal hierarchy precisely because the internal elements are differentiated.
6. **Type has more support than translucency alone.** visionOS uses heavier body/title weights,
   increased tracking, predominantly white text, semantic levels and scale testing; tertiary text
   is reserved for low-legibility needs (§§2.4–2.5). Display-size clock numerals are not a precedent
   for fine text (§5.2).
7. **Color is meaningful and managed, not an all-over painted window.** Spatial guidance asks for
   sparing color in bold text or larger areas; Red Bull TV preserves branding through imagery
   instead of its opaque blue window; clear widgets may desaturate content (§§2.2, 2.6, 5.3).
   The sources do not establish a blanket prohibition on colorful media.
8. **Greater transparency comes with stronger preconditions.** The clear developer variant is
   over rich media, tolerates dimming, and carries bold, bright foregrounds; bright backdrops may
   need the HIG's 35% dark layer, while AVKit may already provide one (§4.1). It is not Apple's
   general-purpose text-heavy surface; regular is the documented choice for that legibility risk.
9. **The material changes or yields when attention and accessibility require it.** Movie passthrough
   dims, modal tasks acquire dimming and opacity, notifications can be tinted, and visionOS can
   replace transparent backgrounds with solid ones (§§2.8, 4.2–4.3). Keeping the glass visibly
   transparent is not an invariant above being able to read and act.
10. **Apple keeps distinct material contracts instead of one universal glass effect.** visionOS
    windows, spatial glass widgets, standard full-screen TV/Watch materials, Liquid Glass controls,
    and pinned clear icons have different behaviors; Dynamic Island explicitly stays opaque
    (§§1, 3, 5). The precedent for a primary glass surface is strongest when its content, backing,
    foreground treatment and environmental behavior are taken together, not when only its sheen
    is borrowed.

## Rules a spatial-register page can be checked against

Each rule is a yes/no reading of the supplied captures and record, with missing state evidence unread rather than passed.

| replaced instrument rule | spatial replacement items |
|---|---|
| r1 — glass only on controls, never content | 2, 25 — content windows/modules, fills inside |
| r3 — small control-only inventory | 2 — one to three task windows/modules |
| r17 — reading content never under glass at rest | 24, 26 — supported reading ink, ornaments outside |
| r20 — content to screen edges, bars above it | 1, 4 — full-bleed environment around windows/modules |
| r21 — safe-area insets and background extension | 16, 26 — inner scroller and attached, separated ornament |

1. `[environment]` The product's full-bleed environment is graded so every window or module's drawn
   body is outside the published-ink dead band and each text line passes its contrast floor in every
   recorded phase and scheme, with source statistics, declared tone and rendered levels
   distinguished in the record. ([HIG
   Materials](https://developer.apple.com/design/human-interface-guidelines/materials), [NN/g,
   Glassmorphism](https://www.nngroup.com/articles/glassmorphism/), spatial memo §§2.1, 6.1;
   `vibrancy.ts`, `vitrea.md` §2)

2. `[layer]` One to three windows or modules are present at rest, each a named unit of the task
   rather than a decorative glass tile. ([WWDC23
   10072](https://developer.apple.com/videos/play/wwdc2023/10072/), [HIG
   Windows](https://developer.apple.com/design/human-interface-guidelines/windows); the count
   ceiling is this register's authoring choice)

3. `[material]` Every window or module has a shorter span of at least 96 CSS px and the family
   shares one recorded thickness from 8 to 14, while ornament labels are judged by rendered contrast
   rather than that span floor. (`references/optics.md` §2, `material.ts` sizeSpanMax; the thickness
   range is an authoring choice grounded in the runtime's surface and morph defaults)

4. `[environment]` The environment is viewport-fixed and remains visible around every window or
   module at rest. ([WWDC23 10072](https://developer.apple.com/videos/play/wwdc2023/10072/), [HIG
   Windows](https://developer.apple.com/design/human-interface-guidelines/windows); spatial memo
   §2.7)

5. `[material]` (= r4) Exactly one variant is in use — regular or clear — across the whole page.
   ([WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/))

6. `[material]` (= r5) Clear glass appears only over media-rich content, and only with a dimming layer
   (≈35% black over bright content).
   ([HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials),
   [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/); spatial memo §4.1 distinguishes this inherited shorthand from the HIG's dark 35% and the API example's black 30%)

7. `[material]` (= r6) At most one control per view carries a tint, and it is the primary action; the tint
   is on the background, not the label.
   ([HIG Color](https://developer.apple.com/design/human-interface-guidelines/color),
   [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/))

8. `[material]` (= r7) No glass surface uses an opaque solid fill or a hand-rolled blur in place of the
   material. ([WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/),
   [WWDC25 284](https://developer.apple.com/videos/play/wwdc2025/284/))

9. `[geometry]` (= r8) Every rounded shape is one of three kinds: fixed radius, capsule (radius = height/2),
   or concentric (radius = parent radius − gap).
   ([WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/))

10. `[geometry]` (= r9) Any element nested inside a rounded container has a radius derived from that
   container, so the two arcs share a centre and no corner reads as pinched or flared.
   ([ConcentricRectangle](https://developer.apple.com/documentation/swiftui/concentricrectangle),
   [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/))

11. `[geometry]` (= r10) Bordered buttons in the floating layer are capsules; small, dense desktop controls
    are rounded rectangles. ([WWDC25 323](https://developer.apple.com/videos/play/wwdc2025/323/),
    [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/))

12. `[grouping]` (= r11) Related bar items share one glass background; unrelated ones sit in separate groups,
    and there are at most three groups per bar.
    ([HIG Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars))

13. `[grouping]` (= r12) No text button shares a glass background with an icon button.
    ([HIG Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars),
    [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/))

14. `[grouping]` (= r13) The material is applied to the control itself, not to its inner views.
    ([WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/))

15. `[grouping]` (= r14) Glass elements that sit near each other belong to one container and read as one
    material, with spacing chosen so they merge or stay separate on purpose.
    ([Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views),
    [WWDC25 323](https://developer.apple.com/videos/play/wwdc2025/323/))

16. `[layout]` (~ r15) Scrolling content is clipped by a child scroller inside its window or module
   with one scroll-edge treatment at its inner edges, while the glass host and its ornaments stay
   still. ([HIG Scroll
   views](https://developer.apple.com/design/human-interface-guidelines/scroll-views), [HIG
   Ornaments](https://developer.apple.com/design/human-interface-guidelines/ornaments); spatial memo
   §2.7)

17. `[material]` (= r16) No glass sits over a flat, uniform background where it would render as an invisible
    outline — glass needs varied content behind it to read as glass. (*secondary*:
    [STRV](https://www.strv.com/blog/how-to-apply-liquid-glass-to-your-app),
    [Six Colors](https://sixcolors.com/post/2025/09/macos-26-tahoe-review-power-under-glass/))

18. `[legibility]` (= r18) Text on glass meets 4.5:1 up to 17 pt and 3:1 at 18 pt or bold, in both light and
    dark. ([HIG Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility))

19. `[legibility]` (= r19) The page still works with reduced transparency, increased contrast and reduced
    motion switched on. ([WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/),
    [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass))

20. `[layout]` (~ r22) No glass host carries a custom background, border or scrim, and the only
   added dimming is painted into the plane beneath clear media glass or a modal task. ([Adopting
   Liquid
   Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass),
   [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/); spatial memo §§4.1–4.2)

21. `[motion]` (= r23) Glass materialises and morphs rather than cross-fading; menus and sheets emerge from
    the control that opened them; press feedback is a glow and slight flex at the pointer, not a
    colour swap. ([WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/),
    [WWDC25 323](https://developer.apple.com/videos/play/wwdc2025/323/))

22. `[colour]` (= r24) Bar and control content is monochrome by default; saturated colour lives in the
    content layer. ([WWDC25 323](https://developer.apple.com/videos/play/wwdc2025/323/),
    [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/))

23. `[colour]` (= r25) No control label uses a colour close to the content passing behind it.
    ([HIG Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars),
    [HIG Color](https://developer.apple.com/design/human-interface-guidelines/color))

24. `[legibility]` Window and module reading text uses primary or secondary ink on children at
   medium or heavier weight with every rendered body line measured at 4.5:1 and the worst line
   gating, while module foregrounds remain bright glance content rather than prose and tertiary or
   quaternary ink carries only decoration. ([WWDC23
   10076](https://developer.apple.com/videos/play/wwdc2023/10076/), [HIG
   Typography](https://developer.apple.com/design/human-interface-guidelines/typography), [WWDC25
   255](https://developer.apple.com/videos/play/wwdc2025/255/); spatial memo §§2.4–2.5, 3)

25. `[layer]` Internal hierarchy uses dark fills for separation or inputs and light fills for
   interactive or selected elements, with no nested glass hosts and no light-on-light stacks.
   ([WWDC23 10076](https://developer.apple.com/videos/play/wwdc2023/10076/), [HIG
   Materials](https://developer.apple.com/design/human-interface-guidelines/materials); spatial memo
   §2.3)

26. `[layer]` Ornaments are separate overlay-plane groups attached to a named window or module, no
   wider than it, outside its edge by the recorded runtime-derived gap on the texture path, with
   controls plain on their housing and no same-plane window overlap. ([HIG
   Ornaments](https://developer.apple.com/design/human-interface-guidelines/ornaments); spatial memo
   §2.7; `group.tsx`, `layer-model.ts`, `samplingPaddingFor`)

27. `[geometry]` Images and video on a window use opaque concentric frames, and any full-colour
   image in a glance module is media smaller than its module. ([HIG
   Widgets](https://developer.apple.com/design/human-interface-guidelines/widgets), [WWDC23
   10076](https://developer.apple.com/videos/play/wwdc2023/10076/); spatial memo §§2.2, 5.3;
   concentric framing is the register's geometry translation)

28. `[colour]` Accents on glass occupy bold text, an entire button or a role-bearing child fill, not
   lightweight type or a thin mark. ([HIG
   Color](https://developer.apple.com/design/human-interface-guidelines/color), [WWDC23
   10076](https://developer.apple.com/videos/play/wwdc2023/10076/); spatial memo §2.6)

29. `[colour]` Windows and modules are untinted, with identity carried by the environment and
   imagery rather than opaque brand-coloured window fills. ([WWDC24
   10086](https://developer.apple.com/videos/play/wwdc2024/10086/), [HIG
   Color](https://developer.apple.com/design/human-interface-guidelines/color); spatial memo §§2.2,
   2.6; untinted windows are this register's composition choice)

30. `[material]` The record and captures show the CSS body actually resolved at the recorded DPR and
   present-host area, both body forms and the forced-colours Canvas panel preserving readable
   content and authored marks, with window-scale extrapolation and any clear optics or dimming
   stated as uncalibrated rather than visionOS fidelity. (Spatial memo §§1, 2.8, 8.9–8.10;
   `css-tier.ts` CSS_TIER_TWO_LAYER_AREA_BUDGET_DEVICE_PX, `css-tier-layers.ts`, `root.ts`;
   `references/optics.md`, The material at window scale)

