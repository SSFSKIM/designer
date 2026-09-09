# Liquid Glass: composing a page in the system

Read this when the material axis has resolved to **glass over planes**, before the composition is
drawn. `references/material.md` owns the axis itself — whether glass is earned here, the plane and
group constraints, the two shipping paths, the accessibility split between runtime and author, and
what `DESIGN.md` records. This file owns the other half: how Apple's system composes a whole screen.
It is a composition language before it is a material — nearly every rule is about which layer a
thing belongs to, what shape it takes, how far apart things sit and what colour is allowed, decided
while the layout is drawn and not in the craft pass. A page that gets the shader right and the
layers wrong does not read as the system; a page that gets the layers right reads as the system even
on the CSS tier. Each rule carries the one source stating it, Apple's own unless marked *secondary*;
where vitrea enforces or diagnoses one, its diagnostic is named and the mechanism is described in
`docs/research/2026-09-10-vitrea-authoring-surface.md` §3 and §6. The taste anchors are the macOS 26
apps — Finder, Safari, Music, Maps, System Settings — so §8 is the reading a desktop page is held
to, and iOS is the source only where a rule is stated there alone.

## 1. The two layers, and how to compose a glass page

A screen here has exactly two planes: content, opaque, filling the window; navigation and controls
floating above it on glass as one distinct functional layer that establishes the visual hierarchy
([HIG Materials][materials]). Glass never appears in the content layer, where a table made of glass
would compete with the content and muddy the hierarchy ([WWDC25 219][wwdc219]), and it is for the
most important functional elements only, which makes the navigation something a reader must see as a
structure distinct from the content ([Adopting Liquid Glass][adopting]); the one exception runs the
other way, a slider knob or switch lifting into glass for the duration of an interaction. vitrea
holds the same line — a glass host inside another is `glass-inside-glass`, an error raised at
registration in both directions and across planes, and a host on a list or table role is
`glass-in-content-layer`, a warning.

**The procedure.** Eight decisions, in order, before any markup. They constrain layout, so none is
fixable later.

1. **Name the live plane.** What fills the window and changes underneath the controls — artwork, a
   map, footage, a photograph, a drawn field. If nothing changes under them, `material.md`'s earning
   test has already failed and this file does not apply.
2. **Inventory the floating layer.** On a desktop page that is a toolbar, a sidebar, and the menus
   and platters opening from them; a tab bar is an iPhone pattern and rarely the right inventory.
   Navigation, the primary action, transient platters, nothing else — a list short enough to read
   aloud, because the count of glass elements is itself a rule and each must be load-bearing ([HIG
   Materials][materials]).
3. **Decide what stays opaque.** Everything not on that list — cards, rows, tables, prose, the
   article read through. Those surfaces declare their own material model underneath and follow it.
4. **Plan the groups.** A group is one backdrop read shared by its members and one material read
   across them; glass cannot sample glass, so neighbours in different containers adapt
   inconsistently ([WWDC25 323][wwdc323]). Group bar items by function and frequency, at most three
   groups per bar, and never a text button in the same group as an icon button, which reads as one
   combined control ([HIG Toolbars][toolbars]). The material goes on the control, never on its inner
   views ([WWDC25 356][wwdc356]). Container spacing is the merge threshold — larger than the layout
   gap and the shapes fuse at rest — so decide per pair whether they merge and space them to say so;
   Apple gives no number, only that relation ([Applying Liquid Glass to custom views][containers]).
   The gap between two *groups* is a different quantity: at least the larger group's effective
   sampling padding, which vitrea derives from the blur it resolved rather than a constant, and
   below which it reports `proxy-overlap-after-enforcement`. Surfaces within one plane must not
   overlap (`same-plane-overlap`, an error); overlap across planes is how a morph works.
5. **Design the backdrop.** The step most pages skip, and the one deciding whether the material is
   visible at all. Over a flat field the blur has nothing to render and the glass becomes invisible
   (*secondary*, [STRV][strv]) — also why most macOS toolbars read as flat grey ovals, Mac apps
   keeping content inside the window rather than letting it slide under the bar. A backdrop needs
   both frequencies, something broad for the lens to bend and something fine for it to displace,
   with the fine part painted *into* the plane, since anything laid over it in CSS is not behind the
   glass and will not be refracted. Where the plane is real content this is already satisfied; check
   that the glass sits over its varied region, not its empty corner. What a group declares about that
   plane — tone and luminance — is an assertion the runtime trusts: out-of-range values clamp with a
   warning, a texture group declares none and lets the runtime read pixels, and a group with neither
   never adapts at all.
6. **Choose the size family.** Larger glass is more opaque to protect legibility, smaller glass
   clearer ([WWDC25 284][wwdc284]), so pick a small set of sizes, one radius per size, one thickness
   across all of them. vitrea's size law runs on the box's short side and is **exactly inert below
   span 32**, saturated at 96; a family living entirely under 32 shows none of the material's size
   behaviour. The demo's three plates at 112 / 68 / 40 with radii 26 / 18 / 12 and a shared
   thickness of 8 straddle that band — one instantiation of the method, not a table to copy. Radii
   are uniform in v1, and four different corner values warn with `non-uniform-radii`.
7. **Place the scroll edge.** Where content passes under a floating bar the transition is a scroll
   edge effect, not a background ([HIG Layout][layout]). The web has no system primitive, so the
   page builds it: a gradient mask on the scrolling content's own edge, one per scrolling view,
   never a darkening scrim under the bar. Put the mask on the scroll container itself — `mask-image`
   on an ancestor of the glass root re-roots the backdrop and demotes the group with `probe-failed`,
   as do `filter`, `backdrop-filter`, `opacity` below 1, `clip-path`, `mix-blend-mode` and a
   `will-change` naming any of them, while `transform`, `contain`, `isolation` and `z-index` were
   measured harmless.
8. **Write the fallback.** The CSS tier, reduced transparency, increased contrast and forced colours
   are states of this design, drawn now rather than repaired once the WebGPU page looks right. The
   composition decision is that hierarchy is carried by layout, grouping and type, so removing the
   material removes an effect and not the structure.

## 2. Variants and tint

Two variants exist, **regular** and **clear**, and they are never mixed in one interface ([WWDC25
219][wwdc219]). Regular is the default and covers nearly everything: it adjusts the luminosity
behind it to hold legibility, and it is the answer whenever a surface carries much text ([HIG
Materials][materials]). Clear is permitted only when Apple's three conditions hold at once — over
media-rich content, a content layer a dimming layer will not harm, bold bright content on the glass
— and it then requires that dimming layer, Apple's figure being black at 35% over bright content.
vitrea refuses mixed variants inside one group; mixed across a page is a defect no runtime catches.

Glass has no colour of its own and takes colour from what is behind it ([HIG Color][color]), so tint
is a rationed exception: at most one tinted control per view, it is the primary action, and the tint
sits on the background rather than the label, since when every element is tinted nothing stands out
([WWDC25 219][wwdc219]). Tint means an adaptive tint, tones mapped against the brightness
underneath, not a solid fill, which is opaque and stops being the material; in vitrea it is a seed
tone-mapped per pixel, one per group, and a second hue is `tint-mixing`, a warning. Everything else
in the control layer is monochrome, which reduces noise and keeps labels legible ([WWDC25
323][wwdc323]); saturated colour lives in the content layer, which on a glass page is the live
plane, where the colour already is.

## 3. Geometry

Use curvature actively. Prefer capsule silhouettes for single-row floating controls and generous,
related curves for larger surfaces. This is the skill's design default, informed by the user's
comparison of the glass demos, not a claim that every native control must be a capsule. Shape,
padding and nested radii should change together so stronger curvature does not crowd the content.

Shape is derived, not chosen. Apple's curvature descends from the hardware bezel, aligning
curvature, size and proportion into one rhythm ([WWDC25 356][wwdc356]); a web page has no bezel it
controls, so the outermost container is the viewport edge or the frame the design draws around the
plane, and every radius inside descends from that. Three shape kinds exist and every element is one
of them: **fixed**, a constant radius; **capsule**, radius exactly half the height; **concentric**,
the parent's radius minus the gap. Concentric does the work — child arc and container arc share a
centre, so the radius is a function of distance from the container's corner and correctly reaches
zero far enough away ([ConcentricRectangle][concentric]) — and a custom component inside a bar must
be concentric with that bar's corners ([HIG Toolbars][toolbars]). The failure signal needs no
measurement: corners reading pinched or flared, usually on a nested container.

Apple publishes no radius values, deliberately — the concentric shape exists so views adapt without
hard-coded values. What a page records is the relation: the container's radius, the gap, the
derivation. The same holds for bar heights and container spacing; there is no number to quote for
either. Start single-row floating bars, search fields, segmented-control housings and standalone
buttons with a capsule. Bordered floating buttons already use that shape in Apple's language
([WWDC25 323][wwdc323]); the skill extends the preference across the floating control layer.
Keep compact inner controls concentric with their housing. Multi-row platters, sidebars and sheets
usually need a generous rounded rectangle to preserve usable space near the corners. Distinguish
the outer glass silhouette from the denser controls inside it rather than making both rectangular
for desktop density.

## 4. Legibility, and the three accessibility modes

The contrast floor is WCAG AA and the material does not negotiate it: 4.5:1 to 17 pt, 3:1 at 18 pt
or bold, in both schemes ([HIG Accessibility][accessibility]). Apple's labels on glass become
vibrant automatically and their colour should not be hand-picked ([WWDC25 323][wwdc323]); on the web
nothing guarantees a ratio, so the measurement is the author's, on rendered pixels across the
backdrop's phases, and content written inside a plane needs its own `color-scheme` or a control on
light glass gets dark-scheme ink whenever the reader's system prefers dark. Small glass flips
between light and dark with what passes behind it while large glass adapts without flipping; on the
web the flip is not something to lean on, so a small control crossing both dark and light regions is
measured at both phases, and if it cannot pass at both it is in the wrong place.

One legibility rule shapes layout rather than styling. At rest — first paint, the top of a scroll —
content should not sit under a glass control at all; reposition or scale so they are separate and
let the intersection happen only while scrolling ([WWDC25 219][wwdc219]).

The three accessibility settings modify the material itself — Reduced Transparency frostier and more
occluding, Increased Contrast pushing elements toward black or white with a contrasting border,
Reduce Motion disabling elastic behaviour — and custom elements do not get this for free ([WWDC25
219][wwdc219]). Treat all three as first-class states: draw them, open them, look at them. Under
forced colours there is no glass at all, and what remains must still be a working interface.

## 5. Layout

Content extends to the edges of the window and the bars float over it; scrollable layouts continue
to the bottom and the sides rather than stopping at the chrome ([HIG Layout][layout]). That is the
most visible difference between a page that reads as the system and one that does not — a bar
sitting *beside* content, in its own band of background, is an ordinary web page wearing the
material.

Content clears the bars by inset, not by a hard offset: Apple's safe area does it and repositions
content when a bar's size changes. A desktop web page has no equivalent — `env(safe-area-inset-*)`
resolves to zero there — so the page owes that guarantee by hand: padding derived from the bar's
measured height plus its margin, recomputed when it changes, never a constant typed once. Where
content genuinely cannot flow beneath a sidebar or inspector, Apple's answer is a background
extension mirroring and blurring the adjacent content instead of a hard edge ([Adopting Liquid
Glass][adopting]); on the web that is hand-built too, and building nothing leaves the material
nothing to sample.

Sidebars are inset and float, with content flowing behind them ([WWDC25 356][wwdc356]). No bar,
sheet or popover gets a custom background, border or darkening layer under it, since a custom
background can overlay or interfere with the material and with the scroll edge — in vitrea a
`background` on a glass host is clobbered every frame by the CSS tier besides. Search belongs at the
toolbar's trailing edge or the top of the sidebar on desktop ([HIG Search fields][search]), and a
tab bar supports navigation and never carries actions ([HIG Tab bars][tab-bars]). The plane is fixed
to the viewport — in vitrea by construction — so a layout where floating chrome and scrolling
content share a scroll container is a design error, not an implementation detail; the demo's answer
is an asymmetric split, the column scrolling and the plane holding the glass fixed.

## 6. Motion

Glass appears and disappears by **materialising**, modulating the light bending and lensing rather
than fading opacity, and between states the controls **morph**, which preserves the sense of one
floating plane ([WWDC25 219][wwdc219]). A cross-fade between two glass surfaces is wrong in every
case: it shows two materials where the language has one. A menu, popover, sheet or dialog emerges
from the control that summoned it, in place ([WWDC25 323][wwdc323]), and an action sheet originates
from its source element rather than the bottom edge. In vitrea a morph is one registered host for
the pair's whole life, interpolating centre, size, radii and thickness on springs; React does this
directly, and on the vanilla path the same composition is one host whose box the page animates,
never a second surface faded in over the first. The trigger inside a platter is a plain button — the
platter is already the material, and nesting is the error the runtime names.

Press feedback is a glow from the point of contact spreading through the element and onto nearby
glass, with a slight scale and flex ([WWDC25 219][wwdc219]) — never a colour swap; vitrea exposes it
as channels on the host (`--vitrea-press`, `--vitrea-glow`, `--vitrea-press-x` and `-y`), so the
decision is where the pointer is, not how to draw a highlight. The system has no idle motion: every
motion Apple describes answers input, a state change or an environmental change. Under Reduce Motion
the elastic behaviour is disabled outright, so no layout may depend on it.

## 7. What the system does not do

Each of these is a rule above, stated as the thing to look for on the built page; the sources are
§§1–6. **Glass on content** — a card, list, panel or hero made of glass — and its commonest form,
**decorative glass cards**, are how a page fails rule 1 while believing it passes. **Glass over
glass** is forbidden outright; anything sitting on glass uses a fill, transparency or vibrancy
instead. Then **translucency everywhere**, the material spreading past the navigation layer; **heavy
or blanket tint**; **a solid fill standing in for tint**, which is opaque and stops being the
material at all; and **a hand-rolled blur** in its place, which is a different thing and shows.

**Decorative bar backgrounds, borders and darkening layers** substitute decoration for the hierarchy
that layout and grouping should carry, and **a scroll edge used as a scrim** — or present where
nothing floats — does the same. **Mixing regular and clear**, and **clear with no dimming over
bright content**, break the material. **Actions in the tab bar** break the navigation. **Hard-coded
radii** are what concentricity exists to replace, and **overflowing toolbars with hand-built
overflow menus** are the layout that produced them. Last, **glass over a uniform field** — the
ghost-glass failure of step 5, invisible in a screenshot of the design file and obvious on the built
page.

## 8. The macOS reading, for a desktop page

The taste anchors are macOS 26's own apps: Finder's window chrome, Safari's toolbar floating over
the page, Music's transport, Maps over its live plane, System Settings' sidebar. The vocabulary is
shared across platforms, the proportions and the chrome are not, and the two layers hold with more
of them visible at once over a larger canvas ([WWDC25 219][wwdc219]).

Concentricity anchors to the **window** corner: controls nest into the window's rounded corners, and
near an edge the shape aligns with that edge rather than taking a capsule with extra margin as it
would on a phone ([WWDC25 356][wwdc356]). For a web page the anchor is whatever the design draws as
the outer frame — the viewport edge, or the plane's own rounded container — and it has to be named,
since a page with no stated anchor has no concentricity to derive. Compact desktop controls can
retain rounded rectangles while their floating housing follows the capsule preference in §3.
Mini, Small and Medium favour horizontal density; Large and X-Large carry more emphasis. The
**hard** scroll edge style is the desktop default,
soft belonging to iOS, and the two are never mixed or stacked. Sidebars float with content extending
beneath them in both panes of a split, each pane carrying at most one scroll edge at consistent
heights ([HIG Sidebars][sidebars]). Menus carry leading-edge icons on macOS now, all items in a
group or none ([HIG Menus][menus]). Search sits at the toolbar's trailing edge or the top of the
sidebar; the bottom-anchored field is an iPhone pattern ([HIG Search fields][search]).

The desktop failure to design against is the one the Tahoe review records: toolbars that do not feel
glassy at all because content stops at the window's inner edge instead of sliding under the bar, and
a transport that reads as cramped and gets partly obscured by content sliding behind it — cramped
plus translucent being the worst combination (*secondary*, [Six Colors][sixcolors]). Both are
composition faults, answered at steps 1 and 5, not by the material.

Two macOS rules have no web equivalent and should not be simulated: leading toolbar items move
inward to clear the window controls ([HIG Windows][windows]), which a web page does not have, so the
leading item aligns to the page's own concentric margin instead; and glass recedes when its window
loses focus, which a page could observe but should not hand-animate, since it would be inventing
motion the system supplies.

## 9. The page's QA list

Twenty-five rules, each answerable yes or no on the rendered page. Run them alongside
`references/qa-protocol.md`, not instead of it, in both colour schemes and once with transparency
reduced. The tags matter to the verdict: a page failing a `[layer]` or `[material]` rule is not this
language whatever else it does, while a `[layout]` or `[legibility]` rule can occasionally be lost
to a web context — record which, and why, rather than passing it silently.

For future authoring, rule 10’s “small, dense desktop controls” means compact inner controls
within a housing, whose rounded rectangles follow the housing’s concentric geometry. That geometry
may reach the capsule limit when the parent radius minus the inset equals half the child height;
r10’s rounded-rectangle wording does not require an inner radius smaller than that capsule limit.
Outer single-row floating housings and standalone floating controls use the capsule default from
§3, including on desktop. This scope preserves the skill’s design preference, not a universal
Apple mandate, and does not reinterpret the frozen panel’s answers.

1. `[layer]` Every glass surface on the page is a navigation or control element; no content surface
   — card, list, panel, hero — uses glass. ([HIG Materials][materials])
2. `[layer]` No glass element is drawn on top of another; anything sitting on glass uses a fill,
   transparency or vibrancy instead. ([WWDC25 219][wwdc219])
3. `[layer]` The count of distinct glass elements on the page is small and each one is load-bearing.
   ([HIG Materials][materials])
4. `[material]` Exactly one variant is in use — regular or clear — across the whole page. ([WWDC25
   219][wwdc219])
5. `[material]` Clear glass appears only over media-rich content, and only with a dimming layer
   (≈35% black over bright content). ([HIG Materials][materials])
6. `[material]` At most one control per view carries a tint, and it is the primary action; the tint
   is on the background, not the label. ([HIG Color][color])
7. `[material]` No glass surface uses an opaque solid fill or a hand-rolled blur in place of the
   material. ([WWDC25 219][wwdc219])
8. `[geometry]` Every rounded shape is one of three kinds: fixed radius, capsule (radius =
   height/2), or concentric (radius = parent radius − gap). ([WWDC25 356][wwdc356])
9. `[geometry]` Any element nested inside a rounded container has a radius derived from that
   container, so the two arcs share a centre and no corner reads as pinched or flared.
   ([ConcentricRectangle][concentric])
10. `[geometry]` Bordered buttons in the floating layer are capsules; small, dense desktop controls
    are rounded rectangles. ([WWDC25 356][wwdc356])
11. `[grouping]` Related bar items share one glass background; unrelated ones sit in separate
    groups, and there are at most three groups per bar. ([HIG Toolbars][toolbars])
12. `[grouping]` No text button shares a glass background with an icon button. ([HIG
    Toolbars][toolbars])
13. `[grouping]` The material is applied to the control itself, not to its inner views. ([WWDC25
    356][wwdc356])
14. `[grouping]` Glass elements that sit near each other belong to one container and read as one
    material, with spacing chosen so they merge or stay separate on purpose. ([Applying Liquid Glass
    to custom views][containers])
15. `[legibility]` A scroll edge effect is present wherever content scrolls under a floating control
    and nowhere else, one per view, with soft and hard styles never mixed or stacked. ([HIG Scroll
    views][scroll-views])
16. `[material]` No glass sits over a flat, uniform background where it would render as an invisible
    outline — glass needs varied content behind it to read as glass. (*secondary*: [STRV][strv])
17. `[legibility]` In the resting state, content does not sit under a glass control at all; the
    layout separates them. ([WWDC25 219][wwdc219])
18. `[legibility]` Text on glass meets 4.5:1 up to 17 pt and 3:1 at 18 pt or bold, in both light and
    dark. ([HIG Accessibility][accessibility])
19. `[legibility]` The page still works with reduced transparency, increased contrast and reduced
    motion switched on. ([Adopting Liquid Glass][adopting])
20. `[layout]` Content reaches the edges of the window; the bars float over it rather than sitting
    beside it. ([HIG Layout][layout])
21. `[layout]` Content clears the floating bars via safe-area insets, and where it cannot flow
    beneath a sidebar it uses a background extension rather than a hard edge. ([HIG Layout][layout])
22. `[layout]` No bar, sheet or popover has a custom background, border or darkening layer added
    under it. ([Adopting Liquid Glass][adopting])
23. `[motion]` Glass materialises and morphs rather than cross-fading; menus and sheets emerge from
    the control that opened them; press feedback is a glow and slight flex at the pointer, not a
    colour swap. ([WWDC25 219][wwdc219])
24. `[colour]` Bar and control content is monochrome by default; saturated colour lives in the
    content layer. ([WWDC25 323][wwdc323])
25. `[colour]` No control label uses a colour close to the content passing behind it. ([HIG
    Toolbars][toolbars])

Rules 15 and 21 name system primitives the web does not have — the scroll edge effect and the
background extension effect, with safe-area insets resolving to zero on desktop. They are answered
by building the equivalent (§1 step 7, §5) and are held to the same yes or no; a page that skipped
them because the platform gave nothing has failed them, not been excused from them.

[materials]: https://developer.apple.com/design/human-interface-guidelines/materials
[toolbars]: https://developer.apple.com/design/human-interface-guidelines/toolbars
[tab-bars]: https://developer.apple.com/design/human-interface-guidelines/tab-bars
[sidebars]: https://developer.apple.com/design/human-interface-guidelines/sidebars
[menus]: https://developer.apple.com/design/human-interface-guidelines/menus
[search]: https://developer.apple.com/design/human-interface-guidelines/search-fields
[scroll-views]: https://developer.apple.com/design/human-interface-guidelines/scroll-views
[layout]: https://developer.apple.com/design/human-interface-guidelines/layout
[color]: https://developer.apple.com/design/human-interface-guidelines/color
[accessibility]: https://developer.apple.com/design/human-interface-guidelines/accessibility
[windows]: https://developer.apple.com/design/human-interface-guidelines/windows
[adopting]: https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass
[containers]: https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views
[concentric]: https://developer.apple.com/documentation/swiftui/concentricrectangle
[wwdc219]: https://developer.apple.com/videos/play/wwdc2025/219/
[wwdc356]: https://developer.apple.com/videos/play/wwdc2025/356/
[wwdc323]: https://developer.apple.com/videos/play/wwdc2025/323/
[wwdc284]: https://developer.apple.com/videos/play/wwdc2025/284/
[strv]: https://www.strv.com/blog/how-to-apply-liquid-glass-to-your-app
[sixcolors]: https://sixcolors.com/post/2025/09/macos-26-tahoe-review-power-under-glass/
