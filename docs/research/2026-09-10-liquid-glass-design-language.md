# Liquid Glass as a design language: the rules for composing a screen

Research memo, 2026-09-10. Written to be distilled into a Claude Code design skill, so every
rule below is phrased as something a page can be checked against, with its source beside it.

**Scope.** This memo is about *composition*, not rendering. How the material refracts, scatters
and tints is the subject of the vitrea runtime and the fidelity ledger; none of that is repeated
here. What follows is the set of decisions a designer makes when laying out a screen in this
language: which layer a thing belongs to, what shape it takes, how far apart things sit, what
colour is allowed, and what the system forbids.

**A note on where Apple's guidance actually lives.** There is no standalone
`human-interface-guidelines/liquid-glass` page — that URL 404s. The normative HIG text for the
material is the *Liquid Glass* section of the **Materials** page, and the adoption checklist is a
Technology Overviews article, **Adopting Liquid Glass**. Component-level rules are spread across
the Toolbars, Tab bars, Sidebars, Buttons, Menus, Search fields, Scroll views, Layout and Color
pages, each of which has a 2025–2026 change-log entry adding Liquid Glass guidance.

**Sources.** Twenty-three Apple sources were opened and read for this memo: the HIG pages for
[Materials](https://developer.apple.com/design/human-interface-guidelines/materials),
[Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars),
[Tab bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars),
[Sidebars](https://developer.apple.com/design/human-interface-guidelines/sidebars),
[Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons),
[Menus](https://developer.apple.com/design/human-interface-guidelines/menus),
[Sheets](https://developer.apple.com/design/human-interface-guidelines/sheets),
[Search fields](https://developer.apple.com/design/human-interface-guidelines/search-fields),
[Scroll views](https://developer.apple.com/design/human-interface-guidelines/scroll-views),
[Layout](https://developer.apple.com/design/human-interface-guidelines/layout),
[Color](https://developer.apple.com/design/human-interface-guidelines/color),
[Typography](https://developer.apple.com/design/human-interface-guidelines/typography),
[Icons](https://developer.apple.com/design/human-interface-guidelines/icons),
[App icons](https://developer.apple.com/design/human-interface-guidelines/app-icons),
[Windows](https://developer.apple.com/design/human-interface-guidelines/windows),
[Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility) and
[Designing for macOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-macos);
the developer articles [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass),
[Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views),
[GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer),
[ConcentricRectangle](https://developer.apple.com/documentation/swiftui/concentricrectangle) and the
[Landmarks sample](https://developer.apple.com/documentation/swiftui/landmarks-building-an-app-with-liquid-glass);
and the full transcripts of WWDC25 sessions
[219 Meet Liquid Glass](https://developer.apple.com/videos/play/wwdc2025/219/),
[356 Get to know the new design system](https://developer.apple.com/videos/play/wwdc2025/356/),
[323 Build a SwiftUI app with the new design](https://developer.apple.com/videos/play/wwdc2025/323/),
[284 Build a UIKit app with the new design](https://developer.apple.com/videos/play/wwdc2025/284/) and
[220 Say hello to the new look of app icons](https://developer.apple.com/videos/play/wwdc2025/220/).
Secondary sources are listed and marked in section 11.

---

## 1. The two layers

The single organising idea of the language is that a screen has exactly two planes. Content is
opaque and fills the window. Navigation and controls float above it on glass. Everything else in
this memo follows from keeping those two planes separate.

- **Liquid Glass belongs to a functional layer of controls and navigation that floats above the
  content layer; the content layer stays on its own plane.** "Liquid Glass forms a distinct
  functional layer for controls and navigation elements — like tab bars and sidebars — that floats
  above the content layer, establishing a clear visual hierarchy between functional elements and
  content." — [HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- **Never put Liquid Glass in the content layer.** "Don't use Liquid Glass in the content layer.
  Liquid Glass works best when it provides a clear distinction between interactive elements and
  content, and including it in the content layer can result in unnecessary complexity and a
  confusing visual hierarchy." — [HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- **Content-layer surfaces — app backgrounds, cards, lists, tables — use standard materials or
  opaque fills, not glass.** — [HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials);
  WWDC 219 puts it concretely: "Consider this tableview: making it Liquid Glass would make it
  compete with other elements and muddy the hierarchy. So keep it in the content layer instead."
  — [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/)
- **There is one sanctioned exception: a control that lives in the content layer may lift into
  glass for the duration of an interaction.** Sliders and switches take on a Liquid Glass
  appearance "to emphasize its interactivity when a person activates it," and the knob "transforms
  into Liquid Glass during interaction."
  — [HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials),
  [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- **Glass is for the most important functional elements only; it is not a general surface
  treatment.** "Use Liquid Glass effects sparingly… Limit these effects to the most important
  functional elements in your app." — [HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials).
  UIKit session: "limit Liquid Glass to the most important elements of your app."
  — [WWDC25 284](https://developer.apple.com/videos/play/wwdc2025/284/)
- **The navigation structure must be legible as a structure distinct from content.** "It's more
  important than ever for your app to have a clear and consistent navigation structure that's
  distinct from the content you provide."
  — [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)

## 2. Variants: regular and clear, tinted and monochrome

- **Two variants exist — regular and clear — and they are never mixed in one interface.** "There
  are two to choose from: Regular and Clear. They should never be mixed, as they each have their
  own characteristics and specific use cases." — [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/)
- **Regular is the default and covers almost every case.** It "blurs and adjusts the luminosity of
  background content to maintain legibility… Most system components use this variant. Use the
  regular variant when background content might create legibility issues, or when components have
  a significant amount of text, such as alerts, sidebars, or popovers."
  — [HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- **Clear is permitted only over visually rich media, and only when all three of Apple's conditions
  hold.** WWDC 219 states them: the element is over media-rich content; the content layer will not
  be harmed by introducing a dimming layer; and the content sitting above the glass is bold and
  bright. — [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/)
- **Clear glass requires a dimming layer behind it when the underlying content is bright — Apple's
  figure is a dark layer at 35% opacity.** "If the underlying content is bright, consider adding a
  dark dimming layer of 35% opacity. If the underlying content is sufficiently dark… you don't need
  to apply a dimming layer." — [HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- **The default state of glass is untinted; it has no colour of its own and takes colour from what
  is behind it.** "By default, Liquid Glass has no inherent color, and instead takes on colors from
  the content directly behind it." — [HIG Color § Liquid Glass color](https://developer.apple.com/design/human-interface-guidelines/color)
- **Tint is reserved for primary actions and status, and applied to the background of the control,
  not to its label.** "To emphasize primary actions, apply color to the background rather than to
  symbols or text… Refrain from adding color to the background of multiple controls."
  — [HIG Color](https://developer.apple.com/design/human-interface-guidelines/color).
  WWDC 219: "Tinting should only be used to bring emphasis to primary elements and actions in the
  UI… Avoid tinting all your elements. When every element is tinted, nothing stands out."
  — [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/)
- **Tint means the system's adaptive tint, not a solid fill.** A solid-filled button "is completely
  opaque and breaks the visual character of Liquid Glass"; the built-in tinting "generates a range
  of tones that are mapped to content brightness underneath the tinted element."
  — [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/)
- **Bar item content defaults to monochrome.** "Icons use monochrome rendering in more places,
  including in toolbars. The monochrome palette reduces visual noise, emphasizes your app's
  content, and maintains legibility. You can still tint icons… but use this to convey meaning,
  like a call to action or next step, but not just for visual effect."
  — [WWDC25 323](https://developer.apple.com/videos/play/wwdc2025/323/)
- **One primary action per bar, on the trailing side, in the prominent style.** "Use the
  `.prominent` style for key actions such as Done or Submit… Only specify one primary action, and
  put it on the trailing side of the toolbar."
  — [HIG Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars)

## 3. Geometry: concentricity, capsules and sizing families

Shape in this system is not decorative. Radii are derived from the container, and the outermost
container is the hardware bezel.

- **Curvature descends from the hardware.** "Apple's hardware features a consistent bezel and that
  same precision now guides the UI, with curvature, size, and proportion aligning to create a
  unified rhythm between what you hold and what you see."
  — [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/)
- **There are exactly three shape types, and every element should be one of them.** "Fixed shapes
  have a constant corner radius. Capsules use a radius that's half the height of the container. And
  concentric shapes calculate their radius by subtracting padding from the parent's."
  — [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/)
- **A nested shape's radius is the parent's radius minus the gap, so the two arcs share a centre.**
  "A rounded corner of a rectangle is concentric relative to the container shape's adjacent corner
  when the corner's radius shares a common center with the containing shape's rounded corner
  radius." — [ConcentricRectangle](https://developer.apple.com/documentation/swiftui/concentricrectangle)
- **Radius is a function of distance from the container corner, not a constant.** "When moving the
  view closer to the container's corner, its corner radius adapts automatically. When moving
  further away the corner radius decreases, to maintain concentricity automatically."
  — [WWDC25 284](https://developer.apple.com/videos/play/wwdc2025/284/). At sufficient distance the
  computed radius may legitimately be zero, i.e. square.
  — [ConcentricRectangle](https://developer.apple.com/documentation/swiftui/concentricrectangle)
- **Bordered buttons are capsules by default.** "Bordered buttons now have a capsule shape by
  default, harmonious with the curved corners of the new design."
  — [WWDC25 323](https://developer.apple.com/videos/play/wwdc2025/323/)
- **On a dense desktop layout, capsules are for standout actions; small controls stay rounded
  rectangles.** "Capsules bring focus and clarity to touch-friendly layouts, but in dense desktop
  environments, they're best used for standout actions. On macOS, Mini, Small, and Medium controls
  will continue using rounded rectangles… Large controls will now use capsule shapes, alongside
  with the new X-Large size." — [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/)
- **Custom components inside a bar must be concentric with that bar's corners.** "By default,
  standard buttons, text fields, headers, and footers have corner radii that are concentric with
  bar corners. If you need to create a custom component, ensure that its corner radius is also
  concentric with the bar's corners." — [HIG Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars)
- **Pinched or flared corners are the failure signal.** "Keep an eye out for corners that feel too
  pinched — or flared. They can create tension and break the sense of balance. One place this often
  shows up in is nested containers — like artwork in a card."
  — [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/)
- **Near a window or display edge, use a concentric shape aligned to that edge; on phones, use a
  capsule with extra margin.** "For phone layouts, use a capsule with extra margin to create space
  near the screen edge. For iPad and Mac, use a concentric shape that aligns with the window edge
  for better balance." — [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/)

## 4. Grouping: one material read per group

`GlassEffectContainer` is the concept that most directly governs layout spacing, because spacing
inside the container decides whether two glass elements read as one shape or two.

- **Multiple glass elements on one screen belong to a container.** "Use GlassEffectContainer when
  applying Liquid Glass effects on multiple views to achieve the best rendering performance. A
  container also allows views with Liquid Glass effects to blend their shapes together and to morph
  in and out of each other during transitions."
  — [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- **The reason is optical, not just performance: glass cannot sample glass.** "The glass material
  reflects and refracts lights, picking colors from nearby content. This effect is achieved by
  sampling content from an area larger than itself. However, glass can not sample other glass, so
  having nearby glass elements in different containers will result in inconsistent behavior. Using
  a glass container allows these elements to share their sampling region, providing a consistent
  visual result." — [WWDC25 323](https://developer.apple.com/videos/play/wwdc2025/323/)
- **A container enforces one material read across its members.** "UIGlassContainerEffect does more
  than just enabling animations. It enforces a uniform adaptation! Glass dynamically adapts to its
  background, but still gets a consistent appearance."
  — [WWDC25 284](https://developer.apple.com/videos/play/wwdc2025/284/)
- **Container spacing is the merge threshold; if it exceeds the layout gap, the shapes fuse at
  rest.** "The larger the spacing value on the container, the sooner the Liquid Glass effects
  behind views blend together… A spacing value on the container that's larger than the spacing of
  an interior HStack, VStack, or other layout container causes Liquid Glass effects to blend
  together at rest because the views are too close to each other."
  — [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- **Apply the material to the control, never to the control's inner views.** "When making custom
  controls, use the same approach, and make sure to apply the material directly to the control, not
  its inner views." — [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/)
- **Never stack glass on glass; use fills, transparency and vibrancy for anything sitting on top of
  glass.** "Always avoid glass on glass. Stacking Liquid Glass elements on top of each other can
  quickly make the interface feel cluttered and confusing. When placing elements on top of Liquid
  Glass, avoid applying the material to both layers. Instead, use fills, transparency, and vibrancy
  for the top elements to make them feel like a thin overlay that is part of the material."
  — [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/)
- **Do not crowd or layer glass elements; prefer standard spacing metrics.** "Prefer to use standard
  spacing metrics instead of overriding them, and avoid overcrowding or layering Liquid Glass
  elements on top of each other."
  — [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- **Group bar items by function and frequency, and aim for at most three groups.** "Group toolbar
  items logically by function and frequency of use… Minimize the number of groups. Too many groups
  of controls can make a toolbar feel cluttered and confusing, even with the added space on iPad
  and Mac. In general, aim for a maximum of three."
  — [HIG Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars)
- **Never put a text button in the same glass group as an icon button.** "Placing an action with a
  text label next to an action with a symbol can create the illusion of a single action with a
  combined text and symbol, leading to confusion and misinterpretation."
  — [HIG Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars). WWDC 356
  repeats it: "be sure to not group symbols with text… since it could be perceived as a single
  button." UIKit's default grouping already separates text buttons, Done/Close and prominent
  buttons onto their own backgrounds.
  — [WWDC25 284](https://developer.apple.com/videos/play/wwdc2025/284/)

## 5. Legibility

- **Text and symbols on glass are vibrant and adapt automatically; do not hand-pick their colour.**
  "SwiftUI automatically uses a vibrant text color that adapts to maintain legibility against
  colorful backgrounds." — [WWDC25 323](https://developer.apple.com/videos/play/wwdc2025/323/).
  "The label automatically becomes vibrant, based on its textColor. This ensures legibility against
  a wide variety of backgrounds." — [WWDC25 284](https://developer.apple.com/videos/play/wwdc2025/284/)
- **Small glass elements flip between light and dark with their backdrop; large ones do not.**
  "Small elements like navbars and tabbars constantly adapt their appearance depending on what's
  behind them. They also flip from light to dark based on the background… Bigger elements, like
  menus or sidebars also adapt based on context, but they don't flip from light to dark. Their
  surface area is too big and transitions like these would be distracting."
  — [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/)
- **Larger glass is more opaque; smaller glass is clearer.** "Glass adapts the appearance based on
  its size. A larger size is more opaque. A smaller size is clearer, and switches between light and
  dark mode automatically, to increase contrast."
  — [WWDC25 284](https://developer.apple.com/videos/play/wwdc2025/284/). HIG: "Liquid Glass appears
  more opaque in larger elements like sidebars to preserve legibility over complex backgrounds."
  — [HIG Color](https://developer.apple.com/design/human-interface-guidelines/color)
- **Where content scrolls under a floating control, a scroll edge effect is required; a background
  is not.** "Instead of a background, use a scroll edge effect to provide a transition between
  content and the control area." — [HIG Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- **The scroll edge effect is a legibility device, not decoration.** "Scroll edge effects aren't
  decorative. They don't block or darken like overlays; they exist to ensure controls stay visually
  distinct." — [HIG Scroll views](https://developer.apple.com/design/human-interface-guidelines/scroll-views).
  WWDC 356 adds that they "shouldn't be used where there aren't any floating UI elements."
  — [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/)
- **One scroll edge effect per view; in split views, one per pane at consistent heights; never mix
  or stack soft and hard styles.** — [HIG Scroll views](https://developer.apple.com/design/human-interface-guidelines/scroll-views),
  [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/)
- **Soft is the iOS default; hard is mostly macOS, for pinned headers, unbackgrounded controls and
  interactive text.** "Soft is the default and the one you'll use in most cases, especially on iOS
  and iPadOS… Hard is mostly used on macOS. It creates a stronger, more opaque boundary — ideal for
  interactive text, controls without backgrounds, or pinned table headers that need extra clarity."
  — [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/)
- **In the resting state, arrange the layout so content does not sit under glass at all.** "In
  steady states, such as when an app first launches, avoid intersections between content and Liquid
  Glass. Instead, reposition or scale the content to maintain separation."
  — [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/). HIG Color: "make sure its
  default or resting state — like the top of a screen of scrollable content — maintains clear
  legibility." — [HIG Color](https://developer.apple.com/design/human-interface-guidelines/color)
- **Where a control layer sits over content, put a system material between them rather than
  directly on the content.** "Like in Safari today, controls sit on top of a system material, not
  directly on content. Without that separation, contrast can suffer."
  — [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/)
- **Contrast floor: WCAG AA — 4.5:1 for text up to 17 pt, 3:1 for 18 pt or bold at any size.**
  — [HIG Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- **The three accessibility settings modify the material, and the design must survive all three.**
  "Reduced Transparency makes Liquid Glass frostier and obscures more of the content behind it.
  Increased contrast makes elements predominantly black or white and highlights them with a
  contrasting border and Reduced Motion decreases the intensity of some effects and disables any
  elastic properties for the material." — [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/).
  Custom elements do not get this for free: "Ensure you test your app's custom elements, colors,
  and animations with different configurations of these settings."
  — [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)

## 6. Layout consequences

- **Content extends to the edges of the window; controls float on top of it.** "Make sure
  backgrounds and full-screen artwork extend to the edges of the display. Also ensure that
  scrollable layouts continue all the way to the bottom and the sides of the device screen.
  Controls and navigation components like sidebars and tab bars appear on top of content rather
  than on the same plane, so it's important for your layout to take this into account."
  — [HIG Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- **Safe areas, not hard offsets, keep content clear of the floating bars.** "A safe area defines
  the area within a view that isn't covered by a toolbar, tab bar, or other views a window might
  provide… safe areas can also help you account for interactive components like bars, dynamically
  repositioning content when sizes change." — [HIG Layout](https://developer.apple.com/design/human-interface-guidelines/layout).
  Adopting Liquid Glass: "audit the safe area compatibility of content next to the sidebar and
  inspector to help make sure underlying content is peeking through appropriately."
  — [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- **Sidebars are inset and float; content flows behind them.** "You will notice sidebars are now
  inset and built with Liquid Glass, allowing content to flow behind them for a more immersive
  feel." — [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/)
- **Where content does not naturally scroll under a sidebar or inspector, use a background
  extension effect rather than a hard edge.** "A background extension effect mirrors the adjacent
  content to give the impression of stretching it under the sidebar, and applies a blur to maintain
  legibility of the sidebar or inspector."
  — [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass);
  the pattern is demonstrated on the Landmarks hero image.
  — [Landmarks](https://developer.apple.com/documentation/swiftui/landmarks-building-an-app-with-liquid-glass)
- **On iOS, search belongs at the bottom when there is room.** "Place search at the bottom if
  there's room. You can either add a search field to an existing toolbar, or as a new toolbar where
  search is the only item… Place search at the top when it's important to defer to content at the
  bottom of the screen, or there's no bottom toolbar."
  — [HIG Search fields](https://developer.apple.com/design/human-interface-guidelines/search-fields)
- **A search tab sits at the trailing end of the tab bar, and the system separates it from the
  other tabs.** "The system automatically separates the search tab from other tabs and places it at
  the trailing end." — [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass);
  "A tab bar can include a dedicated search tab at the trailing end."
  — [HIG Tab bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars)
- **On iPad and Mac, search goes at the trailing edge of the toolbar or the top of the sidebar.**
  "Put a search field at the trailing side of the toolbar for many common uses… Include search at
  the top of the sidebar when filtering content or navigation there."
  — [HIG Search fields](https://developer.apple.com/design/human-interface-guidelines/search-fields)
- **A floating tab bar can minimise on scroll, and only persistent features belong in its accessory
  view.** "Avoid placing screen-specific actions here — a checkout button, for example, belongs with
  the content it supports." — [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/);
  minimise behaviour per [HIG Tab bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars)
- **Do not add your own backgrounds to bars, sheets or popovers.** "Reduce your use of custom
  backgrounds in controls and navigation elements. Any custom backgrounds and appearances you use
  in these elements might overlay or interfere with Liquid Glass or other effects that the system
  provides, such as the scroll edge effect."
  — [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)

## 7. Motion

- **Glass responds to touch and pointer by lighting up from the point of contact.** "When you
  interact with Liquid Glass, the material illuminates from within as a form of feedback. Starting
  right under your fingertips, the glow spreads throughout the element and onto any Liquid Glass
  elements nearby." — [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/)
- **Interactive glass scales, bounces and shimmers on press.** "Glass reacts to user interaction by
  scaling, bouncing, and shimmering, matching the effect provided by toolbar buttons and sliders."
  — [WWDC25 323](https://developer.apple.com/videos/play/wwdc2025/323/)
- **Glass appears and disappears by materialising, never by fading opacity.** "Instead of fading,
  Liquid Glass objects materialize in and out by gradually modulating the light bending and
  lensing." — [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/). UIKit is
  explicit: "Always prefer setting the effect property over the alpha to ensure that the glass
  dematerializes or materializes with the appropriate animation."
  — [WWDC25 284](https://developer.apple.com/videos/play/wwdc2025/284/)
- **Between app states the controls morph rather than cross-fade, preserving the sense of one
  floating plane.** "As you go between states in an app, Liquid Glass dynamically morphs between the
  controls in each context. This maintains the concept of having a singular floating plane that the
  controls live on." — [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/)
- **A menu, popover, sheet or dialog emerges from the control that summoned it, in place.** "When
  showing a menu, the bubble simply pops open to reveal the content contained within. This
  lightweight, in-line transition keeps everything right where you just tapped."
  — [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/); "dialogs also automatically
  morph out of the buttons that present them."
  — [WWDC25 323](https://developer.apple.com/videos/play/wwdc2025/323/)
- **Action sheets originate from their source element, not from the bottom of the screen.** "An
  action sheet originates from the element that initiates the action, instead of from the bottom
  edge of the display." — [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass);
  WWDC 356 frames it as a role: "Now, it springs from the action itself, which serves as the source
  for the action sheet." — [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/)
- **What is not expected: idle motion.** Every motion Apple describes is a response to input, a
  state change, or an environmental change (scroll, focus, device motion). Losing focus makes glass
  recede rather than animate: "when a window loses focus on the Mac or iPad, Liquid Glass shifts its
  appearance and visually recedes to guide attention."
  — [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/)
- **Under Reduce Motion the elastic behaviour is disabled, so no layout may depend on it.**
  — [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/)

## 8. Colour, typography and icons

- **Colour lives in the content layer; the control layer trends monochrome.** "If you want to imbue
  color into your app, do it in the content layer instead."
  — [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/). HIG: "If your app features
  colorful backgrounds or visually rich content, prefer a monochromatic appearance for toolbars and
  tab bars, or choose an accent color with sufficient visual differentiation."
  — [HIG Color](https://developer.apple.com/design/human-interface-guidelines/color)
- **Do not use a control-label colour that is close to the content behind it.** "Avoid applying a
  similar color to toolbar item labels and content layer backgrounds."
  — [HIG Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars); same rule
  stated on [Tab bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars) and
  [Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons)
- **The accent colour's job is the one prominent action.** "The system applies the app accent color
  to the background in prominent buttons — such as the Done button — to draw attention and elevate
  their visual prominence." — [HIG Color](https://developer.apple.com/design/human-interface-guidelines/color).
  Keep prominent buttons to "one or two per view."
  — [HIG Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons)
- **Custom colours need light, dark and increased-contrast variants.** "If you do apply color to
  these elements, leverage system colors, or define a custom color with light and dark variants, and
  an increased contrast option for each variant."
  — [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- **Type got bolder and left-aligned at key moments.** "Typography has been refined to strengthen
  clarity and structure, now bolder and left-aligned to improve readability in key moments like
  alerts and onboarding." — [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/)
- **Avoid light weights; prefer Regular through Bold.** "Prefer Regular, Medium, Semibold, or Bold
  font weights, and avoid Ultralight, Thin, and Light font weights."
  — [HIG Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- **The macOS text-style ladder is the sizing reference for desktop chrome** (from the HIG
  specification table): Body 13 pt / Regular (emphasised Semibold), Headline 13 pt / Bold, Callout
  12 pt, Subheadline 11 pt, Footnote and Caption 1 10 pt, Title 3 15 pt, Title 2 17 pt, Title 1
  22 pt, Large Title 26 pt. — [HIG Typography § macOS built-in text styles](https://developer.apple.com/design/human-interface-guidelines/typography)
- **Prefer symbols over text in bars, but never for actions a symbol cannot name.** "Prefer simple,
  recognizable symbols for items instead of text, except for actions like edit that aren't
  well-represented by symbols."
  — [HIG Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars). WWDC 356:
  "When there's no clear shorthand, a text label is always the better choice."
  — [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/)
- **App icons are layered, and the system — not the designer — supplies the glass effects.** "Let the
  system handle applying masking, blurring, and other visual effects, rather than factoring them
  into your design… The system automatically applies effects like reflection, refraction, shadow,
  blur, and highlights to your icon layers."
  — [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- **Strip baked-in effects from icon artwork; simplify; avoid thin lines and sharp edges.** "We also
  recommend pairing back any built-in static effects in your source artwork… Ideally, sharp edges
  and thin lines should be avoided. Instead, using rounder corners makes it easier for the light to
  seamlessly travel on the edges of an element."
  — [WWDC25 220](https://developer.apple.com/videos/play/wwdc2025/220/); "Prefer clearly defined
  edges in foreground layers… avoid soft and feathered edges."
  — [HIG App icons](https://developer.apple.com/design/human-interface-guidelines/app-icons)

## 9. What the system does not do

Each anti-pattern below is named or directly implied by a primary source, and each restates a rule
from an earlier section as the thing to look for.

- **Glass on content** — a card, list, panel or hero made of glass "would make it compete with other
  elements and muddy the hierarchy." ([WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/))
- **Glass over glass** — explicitly forbidden; use fills, transparency and vibrancy on top instead.
  ([WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/))
- **Translucency everywhere** — "it is best reserved for the navigation layer."
  ([WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/))
- **Heavy or blanket tinting** — "When every element is tinted, nothing stands out."
  ([WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/))
- **A solid fill standing in for tint** — it "breaks the visual character of Liquid Glass."
  ([WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/))
- **A custom blur in place of the system material** — glass "is distinct from other visual effects,
  like UIBlurEffect" ([WWDC25 284](https://developer.apple.com/videos/play/wwdc2025/284/)), and
  materials are chosen by semantic meaning, never by the colour they impart
  ([HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials)).
- **Decorative bar backgrounds, borders and darkening layers** — "hierarchy should be expressed
  through layout and grouping." ([WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/))
- **A scroll edge effect used as a scrim** — it is not an overlay and must not appear where nothing
  floats. ([HIG Scroll views](https://developer.apple.com/design/human-interface-guidelines/scroll-views))
- **Mixing regular and clear** — "They should never be mixed."
  ([WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/))
- **Clear glass with no dimming over bright content** — "legibility gets noticeably worse."
  ([WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/))
- **Actions in the tab bar** — "Use a tab bar to support navigation, not to provide actions."
  ([HIG Tab bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars))
- **Hard-coded radii and layout metrics** — the concentric shape exists so views "adapt correctly
  across devices and sizes without hard-coded values."
  ([ConcentricRectangle](https://developer.apple.com/documentation/swiftui/concentricrectangle))
- **Overflowing toolbars and hand-built overflow menus** — "Don't add an overflow menu manually, and
  avoid layouts that cause toolbar items to overflow by default."
  ([HIG Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars))

## 10. macOS versus iOS

Since the demos are desktop pages, the macOS reading of the language matters more than the iPhone
one. The vocabulary is shared; the proportions and the chrome are not.

- **Same two layers, more of them at once.** "On iPad and Mac, we've applied these very same
  principles. Just like on iPhone, these Liquid Glass layers form a distinct functional layer for
  controls and navigation, floating above everything and giving you a larger, more expansive canvas
  for your content." — [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/)
- **Window corners, not device corners, are the concentricity anchor.** "Windows adopt rounder
  corners to fit controls and navigation elements… Glass controls nest perfectly into the rounded
  corners of windows, maintaining concentricity throughout the UI."
  — [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass),
  [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/). On desktop, use "a concentric
  shape that aligns with the window edge." — [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/)
- **Compact controls stay rectangular on desktop.** Mini, Small and Medium controls keep rounded
  rectangles for horizontal density; Large and the new X-Large use capsules and carry emphasis.
  — [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/),
  [WWDC25 323](https://developer.apple.com/videos/play/wwdc2025/323/)
- **The hard scroll edge effect is the desktop default case.** Soft belongs to iOS; hard "is mostly
  used on macOS" for pinned headers, interactive text and unbackgrounded controls.
  — [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/)
- **Sidebars float and content extends beneath them, in both split-view panes.** Each pane may carry
  its own scroll edge effect, kept at consistent heights.
  — [HIG Sidebars](https://developer.apple.com/design/human-interface-guidelines/sidebars),
  [HIG Scroll views](https://developer.apple.com/design/human-interface-guidelines/scroll-views)
- **Window controls occupy the leading edge of the toolbar, so leading toolbar items must move
  inward.** "If your app has toolbar buttons at the leading edge, they might be hidden by window
  controls when they appear. To prevent this, instead of placing buttons directly on the leading
  edge, move them inward." — [HIG Windows](https://developer.apple.com/design/human-interface-guidelines/windows)
- **Inactive windows recede.** Glass "shifts its appearance and visually recedes" on focus loss
  ([WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/)), consistent with the
  long-standing rule that inactive windows do not use materials
  ([HIG Windows](https://developer.apple.com/design/human-interface-guidelines/windows)).
- **Menus gained icons on macOS and aligned their anatomy with iOS.** "Icons are consistently on the
  leading edge and are now used on macOS too."
  — [WWDC25 323](https://developer.apple.com/videos/play/wwdc2025/323/). Provide icons for all items
  in a group or none. — [HIG Menus](https://developer.apple.com/design/human-interface-guidelines/menus)
- **Search sits at the toolbar's trailing edge or the top of the sidebar — not at the bottom.** The
  bottom-anchored search field is an iPhone pattern.
  — [HIG Search fields](https://developer.apple.com/design/human-interface-guidelines/search-fields)

## 11. Secondary readings — what practitioners found (not Apple)

Everything above is Apple's own guidance. This section is **secondary**: working designers and
reviewers documenting how the language behaves in practice. It is included because two of its
findings are things Apple never says, and both matter for desktop web pages.

**Ghost glass — glass over a flat background renders as nothing.** "Glass only works when there is
rich, varied content behind it. On a plain white or monochromatic background, the blur has nothing
to render, and the glass becomes invisible… Always make sure that glass elements are positioned
above content that has color, texture or motion behind them." Same source on backdrop extension:
"Content behind a glass bar should be allowed to scroll or render underneath it, not stop at the
edge of the bar. Without it, the glass surface has nothing interesting to render and falls flat."
And on compounding: "Placing a glass element directly on top of another glass surface causes the
blur to compound"; the fix is "a different material or a solid tint."
— *secondary*, Tom Naute, [How to Apply Liquid Glass to Your App, STRV](https://www.strv.com/blog/how-to-apply-liquid-glass-to-your-app)

**The same failure, observed on macOS.** "Most Liquid Glass toolbars don't feel glassy at all" — in
Finder they read as "flat light gray ovals separated from a featureless white or gray expanse by a
generic drop shadow," because Mac apps typically keep content inside the window rather than sliding
it under the toolbar, so the material has nothing to sample. Where content *does* pass under an
unbacked floating bar, "similarly-colored content sliding under a button can make it illegible,"
and the system compensates by "changing the color of the text or the opacity and brightness of the
background item" — which "mostly succeeds, though changes in the appearance of the buttons can be
distracting." Cramped plus translucent is the worst combination: Music's bottom controller "feels
cramped and can get partially obscured by content sliding behind it."
— *secondary*, Jason Snell, [macOS 26 Tahoe review: Power under glass, Six Colors](https://sixcolors.com/post/2025/09/macos-26-tahoe-review-power-under-glass/)

**The usability objections, stated as heuristics worth checking against.** The governing principle
is that "anything placed on top of something else becomes harder to see," so translucency is a
legibility cost that something has to pay for. Specific findings: text over images loses contrast;
blurring the backdrop is not sufficient mitigation (Maps' bottom icons still merge with food photos
"even though the background is blurred"); one translucent surface must never overlap another's live
text; floating controls "work best when they stand out clearly — not when they blend in"; and
controls that change size or position by context make the interface "harder to learn and less
predictable."
— *secondary*, Raluca Budiu, [Liquid Glass Is Cracked, and Usability Suffers in iOS 26, NN/g](https://www.nngroup.com/articles/liquid-glass/)

**The craft critique — what breaks when everything shares one material.** "Title bars merged with
toolbars. Toolbars merged with tab bars… Is this icon an action or a tab? Will it open a menu or
switch the view? It's anybody's guess." Related observations: inconsistent elevation within one
system ("Some sidebars float while others don't"), lost drag affordances ("titlebars… are now
imperceptible"), and containers that "don't know where to end." The lesson is that one material
cannot by itself carry the distinctions that borders and bars used to carry; grouping, spacing and
placement have to do that work.
— *secondary*, Louie Mantia, [I've Got Better Things To Do Than This, and Yet](https://lmnt.me/blog/ive-got-better-things-to-do-than-this-and-yet.html)

**Apple moved the dial during the betas, then handed it to users.** Beta 3 made navigation bars
markedly more opaque across many apps and raised the backdrop-luminance threshold at which glass
inverts to its dark tone; beta 4 restored some translucency
([MacRumors](https://www.macrumors.com/guide/ios-26-beta-3-liquid-glass-changes/),
[9to5Mac](https://9to5mac.com/2025/07/22/ios-26-beta-4-adds-more-liquid-back-to-liquid-glass-design/)).
The eventual answer was a user-facing Clear/Tinted choice rather than one global value. The design
consequence: a page must stay legible at both ends of that range, not be tuned to one opacity.
— *secondary*

**One widely quoted number to avoid repeating.** A June 2025 post reporting a 1.5:1 contrast
measurement on iOS 26 screens is the most-cited figure in the debate, but it names no screen, gives
no method, and predates the beta opacity increases
([Infinum](https://infinum.com/blog/apples-ios-26-liquid-glass-sleek-shiny-and-questionably-accessible/)).
Treat it as unreproducible; use Apple's own 4.5:1 / 3:1 floor instead. — *secondary*

Also read: [Getting Clarity on Apple's Liquid Glass, CSS-Tricks](https://css-tricks.com/getting-clarity-on-apples-liquid-glass/)
(why refraction makes contrast structurally harder than blur does),
[The Accessibility Challenges of iPhone's New Liquid Glass Design, Access Advisors](https://accessadvisors.nz/blog/liquid-glass)
(consistency of contrast across backdrops, not peak contrast, is the metric), and
[Liquid Glass on the Web, Chris Coyier](https://blog.master.dev/liquid-glass-on-the-web/)
(heavy blur is legibility-safe; light tint plus strong displacement is where text breaks).

## Rules a page can be checked against

Each rule is one thing a reviewer can look for on a rendered page and answer yes or no.

1. `[layer]` Every glass surface on the page is a navigation or control element; no content
   surface — card, list, panel, hero — uses glass.
   ([HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials))
2. `[layer]` No glass element is drawn on top of another; anything sitting on glass uses a fill,
   transparency or vibrancy instead. ([WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/))
3. `[layer]` The count of distinct glass elements on the page is small and each one is load-bearing.
   ([HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials),
   [WWDC25 284](https://developer.apple.com/videos/play/wwdc2025/284/))
4. `[material]` Exactly one variant is in use — regular or clear — across the whole page.
   ([WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/))
5. `[material]` Clear glass appears only over media-rich content, and only with a dimming layer
   (≈35% black over bright content).
   ([HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials),
   [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/))
6. `[material]` At most one control per view carries a tint, and it is the primary action; the tint
   is on the background, not the label.
   ([HIG Color](https://developer.apple.com/design/human-interface-guidelines/color),
   [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/))
7. `[material]` No glass surface uses an opaque solid fill or a hand-rolled blur in place of the
   material. ([WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/),
   [WWDC25 284](https://developer.apple.com/videos/play/wwdc2025/284/))
8. `[geometry]` Every rounded shape is one of three kinds: fixed radius, capsule (radius = height/2),
   or concentric (radius = parent radius − gap).
   ([WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/))
9. `[geometry]` Any element nested inside a rounded container has a radius derived from that
   container, so the two arcs share a centre and no corner reads as pinched or flared.
   ([ConcentricRectangle](https://developer.apple.com/documentation/swiftui/concentricrectangle),
   [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/))
10. `[geometry]` Bordered buttons in the floating layer are capsules; small, dense desktop controls
    are rounded rectangles. ([WWDC25 323](https://developer.apple.com/videos/play/wwdc2025/323/),
    [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/))
11. `[grouping]` Related bar items share one glass background; unrelated ones sit in separate groups,
    and there are at most three groups per bar.
    ([HIG Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars))
12. `[grouping]` No text button shares a glass background with an icon button.
    ([HIG Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars),
    [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/))
13. `[grouping]` The material is applied to the control itself, not to its inner views.
    ([WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/))
14. `[grouping]` Glass elements that sit near each other belong to one container and read as one
    material, with spacing chosen so they merge or stay separate on purpose.
    ([Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views),
    [WWDC25 323](https://developer.apple.com/videos/play/wwdc2025/323/))
15. `[legibility]` A scroll edge effect is present wherever content scrolls under a floating
    control and nowhere else, one per view, with soft and hard styles never mixed or stacked.
    ([HIG Scroll views](https://developer.apple.com/design/human-interface-guidelines/scroll-views),
    [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/))
16. `[material]` No glass sits over a flat, uniform background where it would render as an invisible
    outline — glass needs varied content behind it to read as glass. (*secondary*:
    [STRV](https://www.strv.com/blog/how-to-apply-liquid-glass-to-your-app),
    [Six Colors](https://sixcolors.com/post/2025/09/macos-26-tahoe-review-power-under-glass/))
17. `[legibility]` In the resting state, content does not sit under a glass control at all; the
    layout separates them. ([WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/))
18. `[legibility]` Text on glass meets 4.5:1 up to 17 pt and 3:1 at 18 pt or bold, in both light and
    dark. ([HIG Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility))
19. `[legibility]` The page still works with reduced transparency, increased contrast and reduced
    motion switched on. ([WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/),
    [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass))
20. `[layout]` Content reaches the edges of the window; the bars float over it rather than sitting
    beside it. ([HIG Layout](https://developer.apple.com/design/human-interface-guidelines/layout))
21. `[layout]` Content clears the floating bars via safe-area insets, and where it cannot flow
    beneath a sidebar it uses a background extension rather than a hard edge.
    ([HIG Layout](https://developer.apple.com/design/human-interface-guidelines/layout),
    [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass))
22. `[layout]` No bar, sheet or popover has a custom background, border or darkening layer added
    under it. ([Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass),
    [WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/))
23. `[motion]` Glass materialises and morphs rather than cross-fading; menus and sheets emerge from
    the control that opened them; press feedback is a glow and slight flex at the pointer, not a
    colour swap. ([WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/),
    [WWDC25 323](https://developer.apple.com/videos/play/wwdc2025/323/))
24. `[colour]` Bar and control content is monochrome by default; saturated colour lives in the
    content layer. ([WWDC25 323](https://developer.apple.com/videos/play/wwdc2025/323/),
    [WWDC25 219](https://developer.apple.com/videos/play/wwdc2025/219/))
25. `[colour]` No control label uses a colour close to the content passing behind it.
    ([HIG Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars),
    [HIG Color](https://developer.apple.com/design/human-interface-guidelines/color))
