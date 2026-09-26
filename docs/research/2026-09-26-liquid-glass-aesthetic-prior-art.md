# Liquid Glass: prior art on its aesthetics and design philosophy

> Research report, 2026-09-26, collected by a research agent for the materialist skill
> (`skills/materialist/SKILL.md`; spec `docs/doperpowers/specs/2026-09-26-materialist-skill.md`).
> Companion to `2026-09-10-liquid-glass-design-language.md`, which holds Apple's composition rules;
> this report holds the aesthetic articulation, the lineage, the critique and the motion character.
> Not loaded at plugin runtime. Quotes were pulled through a fetch-and-extract tool during the
> session and transcript typos are kept; check any quote against its source before publishing it
> word for word. The 27 releases shipped on 2026-09-14.

---

## 1. How Apple describes it

### 1.1 What the material is

- **A "meta-material" defined by lensing, not blur.**
  - "Liquid Glass is a new digital meta-material that dynamically bends and shapes light." ([WWDC25 219, Meet Liquid Glass](https://developer.apple.com/videos/play/wwdc2025/219/))
  - "The primary way Liquid Glass visually defines itself is through something called Lensing." (same)
  - "Where as previous materials scattered light, this new set of materials dynamically bends, shapes, and concentrates light in real time." (same)
- **It adapts to what is behind it, and it defers to that content.**
  - "Its primary goal is to remain visually clear, deferring to the content underneath." (219)
- **Larger pieces read as thicker glass.**
  - "When glass flexes and morphs to larger sizes … its material characteristics change to simulate a thicker, more substantial material." (219)
  - "A larger size is more opaque." ([WWDC25 284](https://developer.apple.com/videos/play/wwdc2025/284/))
  - "Bigger elements, like menus or sidebars … don't flip from light to dark. Their surface area is too big and transitions like these would be distracting." (219)
- **Newsroom copy.**
  - "This translucent material reflects and refracts its surroundings"
  - "Its color is informed by surrounding content and intelligently adapts between light and dark environments."
  - Alan Dye: "It combines the optical qualities of glass with a fluidity only Apple can achieve … as it transforms depending on your content or context"
  - Source: [Apple Newsroom, 2025-06-09](https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/)
- **The UIKit session's summary:** "It is translucent, dynamic and alive." ([284](https://developer.apple.com/videos/play/wwdc2025/284/))
- **It also expresses focus.** "when a window loses focus on the Mac or iPad, Liquid Glass shifts its appearance and visually recedes to guide attention." (219)

### 1.2 Where it belongs: the two-layer model

- **Glass is the navigation and controls layer. It never goes in the content layer.**
  - HIG: "Liquid Glass forms a distinct functional layer for controls and navigation elements … that floats above the content layer."
  - HIG, verbatim: "**Don't use Liquid Glass in the content layer.**"
  - Source: [HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
  - The one exception is transient content-layer controls such as sliders and toggles, which "take on a Liquid Glass appearance to emphasize its interactivity when a person activates it" (same).
  - "You may be tempted to use Liquid Glass everywhere but it is best reserved for the navigation layer that floats above the content of your app." (219)
  - On making a table view glass: it "would make it compete with other elements and muddy the hierarchy." (219)
- **Use it sparingly.**
  - "Avoid overusing Liquid Glass effects … Limit these effects to the most important functional elements in your app." ([Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass))
  - "limit Liquid Glass to the most important elements of your app. Where possible, use the system views and controls" ([284](https://developer.apple.com/videos/play/wwdc2025/284/))
- **The UI should get out of the way when it isn't needed.**
  - "the UI should support interaction where needed, and remain unobtrusive when it's not." ([WWDC25 356](https://developer.apple.com/videos/play/wwdc2025/356/))
  - "floating above your content to bring structure and clarity, without ever stealing focus." (356)
- **WWDC26 restates the model for branding.**
  - "Think of your app as two distinct layers: the UI layer, which serves as the global navigation, and the content layer" ([WWDC26 251](https://developer.apple.com/videos/play/wwdc2026/251/))
  - "Conceptually, the content layer is the best opportunity to express your brand identity." (251)

### 1.3 Hierarchy rules

- **No glass on glass.**
  - "always avoid glass on glass Stacking Liquid Glass elements on top of each other can quickly make the interface feel cluttered and confusing." (219)
  - For anything placed on glass: "use fills, transparency, and vibrancy for the top elements to make them feel like a thin overlay that is part of the material." (219)
  - Apple Maps removes its floating buttons when a sheet expands, which "keeps the illusion of a single floating layer of glass intact." (284)
- **Keep the resting state clean.**
  - "In steady states, such as when an app first launches, avoid intersections between content and Liquid Glass." (219)
  - "make sure its default or resting state — like the top of a screen of scrollable content — maintains clear legibility." ([HIG Color](https://developer.apple.com/design/human-interface-guidelines/color))
- **Build hierarchy from layout, not ornament.**
  - "Instead of relying on decoration, hierarchy should be expressed through layout and grouping." (356)
- **Apply glass to the control itself.**
  - "make sure to apply the material directly to the control, not its inner views." (356)

### 1.4 The Regular and Clear variants

- **Never mix them.** "They should never be mixed … Regular is the most versatile and the one you will be using the most." (219)
- **Regular** is for text-heavy or legibility-risky surfaces: "Use the regular variant when background content might create legibility issues, or when components have a significant amount of text, such as alerts, sidebars, or popovers." ([HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials))
- **Clear** is only for rich media:
  - "**Only use clear Liquid Glass for components that appear over visually rich backgrounds.**" (HIG)
  - "Clear, on the other hand, does not have adaptive behaviors." (219)
  - It needs a dimming layer: "consider adding a dark dimming layer of 35% opacity" when the content is bright (HIG).
  - Apple's three conditions for Clear: the element sits over media-rich content, a dimming layer won't hurt the content, and "the content sitting above it is bold and bright." (219)

### 1.5 Colour and tint

- **Glass is colourless by default.**
  - "By default, Liquid Glass has no inherent color, and instead takes on colors from the content directly behind it." ([HIG Color](https://developer.apple.com/design/human-interface-guidelines/color))
  - Symbols and text on small glass elements "follow a monochromatic color scheme" by default (same).
- **Tint is for emphasis only.**
  - "Tinting should only be used to bring emphasis to primary elements and actions in the UI. When every element is tinted, nothing stands out" (219)
  - HIG: "To emphasize primary actions, apply color to the background rather than to symbols or text … Refrain from adding color to the background of multiple controls."
  - "Keep the number of prominent buttons to one or two per view." ([HIG Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons))
  - Toolbars: "Only specify one primary action, and put it on the trailing side of the toolbar." ([HIG Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars))
- **A solid fill is not a tint.** Apple showed a solid-filled button and said it "is completely opaque and breaks the visual character of Liquid Glass." (219)
- **Colour belongs in the content layer.**
  - "If you want to imbue color into your app, do it in the content layer instead." (219)
  - "move color into the content area of your app, into the scroll view … Liquid Glass controls sit above the content layer and pick up your brand color dynamically." ([WWDC26 251](https://developer.apple.com/videos/play/wwdc2026/251/))
- **Avoid colour collisions with content.** Over colourful content, "prefer a monochromatic appearance for toolbars and tab bars, or choose an accent color with sufficient visual differentiation." (HIG Color)
- **Monochrome icons are the default in bars.** "The monochrome palette reduces visual noise, emphasizes your app's content, and maintains legibility." ([WWDC25 323](https://developer.apple.com/videos/play/wwdc2025/323/))
- **Supply every colour variant.** "Even if your app ships in a single appearance mode, provide both light and dark colors to support Liquid Glass adaptivity" (HIG Color)

### 1.6 Legibility, typography, vibrancy and scroll edge effects

- **Scroll edge effects.**
  - They "gently dissolve the content into the background, lifting the glass visually above the moving content" (219).
  - They are structural, not decorative: "scroll edge effects are not decorative … shouldn't be used where there aren't any floating UI elements." (356)
  - "Apply one scroll edge effect per view." (356)
  - The HIG was updated in June 2026: "**Prefer the automatic scroll edge effect style.**" It gives "more opaque visual separation for top toolbars that contain a large number of controls, text that appears outside of Liquid Glass controls, and pinned table headers." ([HIG Scroll views](https://developer.apple.com/design/human-interface-guidelines/scroll-views))
- **Typography.**
  - Type is "now bolder and left-aligned to improve readability in key moments like alerts and onboarding." (356)
  - "**In general, avoid light font weights.**" ([HIG Typography](https://developer.apple.com/design/human-interface-guidelines/typography))
- **Vibrancy.** "use vibrant colors on top of it." (HIG Materials)
- **Accessibility settings reshape the material.**
  - "Reduced Transparency, makes Liquid Glass frostier … Increased contrast, makes elements predominantly black or white … Reduced Motion … disables any elastic properties for the material." (219)
  - Apple's instruction: "Test your interface with a variety of display and accessibility settings." ([Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass))

### 1.7 Composition of bars, groups and sheets

- **Grouping.**
  - "Group bar items by function and frequency." (356)
  - Don't group symbols with text, "since it could be perceived as a single button." (356)
  - "When there's no clear shorthand, a text label is always the better choice." (356)
  - "**Minimize the number of groups** … aim for a maximum of three." (HIG Toolbars)
- **Crowding.** "If your bar is feeling too crowded, use it as a cue to remove anything unnecessary" (356)
- **Tab bars hold navigation, not screen actions.** "Avoid placing screen-specific actions here—a checkout button, for example, belongs with the content it supports." (356)
- **Sheets.**
  - "When a task interrupts the main flow, pair Liquid Glass with a dimming layer … when a task happens in parallel, Liquid Glass creates a natural separation" (356)
  - A half sheet that expands to full height "transitions to a more opaque appearance to help maintain focus on the task." (Adopting)

### 1.8 Apple's stated intent and principles

- **The three pillars.** "establish hierarchy, create harmony, and maintain consistency across devices and platforms." ([Technology overview: Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/liquid-glass))
  - The same page adds: be judicious with colour "so they stay legible and allow your content to infuse them and shine through."
- **Harmony as a metaphor.** "Think of it like playing in the same music key—your interface elements should complement the system's rhythm and tone, not clash with it." (356)
- **Newsroom framing.** "establishing greater harmony between hardware, software, and content" ([Newsroom](https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/))
- **Principles reintroduced in 2026.** Apple added a Design Principles page to the HIG on 2026-06-08. The eight principles are Purpose, Agency, Responsibility, Familiarity, Flexibility, Simplicity, Craft and Delight ([HIG Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)). The companion session says:
  - "When we say simple, we don't mean minimal."
  - "In a simple interface, every element earns its place."
  - "When your hierarchy is strong, the most important item on the screen is always the most obvious one."
  - Source: [WWDC26 250](https://developer.apple.com/videos/play/wwdc2026/250/)
- **Branding under the new design.** Custom utilitarian components "can make the product appear less native - or even dated". The advice is "exercise restraint — use it sparingly and with intention". ([WWDC26 251](https://developer.apple.com/videos/play/wwdc2026/251/))

### 1.9 The 2026 refinements, and what they concede

- **Keynote framing** (speaker introduced only as "Shubham"): "there's a natural process where we take a bold leap forward and then we continue to iterate." ([WWDC26 Keynote](https://developer.apple.com/videos/play/wwdc2026/101/))
- **Changes stated in the Platforms State of the Union** ([WWDC26 102](https://developer.apple.com/videos/play/wwdc2026/102/)):
  - Diffusion and edges: glass now "more effectively diffuses complex content behind it" and adds "a darkened edge along with brighter specular highlights."
  - A user slider "anywhere from ultra clear to fully tinted".
  - Sidebars "expand to the edges on Mac and iPad".
  - Sidebar icons "regain their color".
  - "the same tighter corner radius" for every macOS window.
  - A "uniform toolbar" when content scrolls under floating bars.
  - Menu icons are now "hidden by default", with an API to show them for key actions.
- **Stated goal:** "reincorporate some of the cornerstones of macOS design that our users have always loved" (Keynote).
- **What this concedes:** in dense desktop contexts, Apple moved back toward more structure, more opacity and less spectacle.

---

## 2. Shape and geometry

- **Hardware sets the geometry.**
  - "curvature, size, and proportion aligning to create a unified rhythm between what you hold and what you see." ([356](https://developer.apple.com/videos/play/wwdc2025/356/))
  - "The shape of the hardware informs the curvature of controls, so many controls adopt rounder forms to elegantly nestle into the corners of windows and displays." ([Adopting](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass))
- **Three shape types** (all from 356):
  - "There's a quiet geometry to how our shapes fit together, driven by concentricity."
  - "fixed shapes have a constant corner radius."
  - "Capsules use a radius that's half the height of the container."
  - "concentric shapes calculate their radius by subtracting padding from the parent's."
- **The failure mode to watch for:** "keep an eye out for corners that feel too pinched— or flared." (356)
- **Placement by platform:**
  - "For phone layouts, use a capsule with extra margin … For iPad and Mac, use a concentric shape that aligns with the window edge" (356)
  - "a button that is positioned at the bottom of a sheet should share the same corner center with the corners of the sheet." ([323](https://developer.apple.com/videos/play/wwdc2025/323/))
- **Radius varies with distance from the container's corner.**
  - "When moving further away the corner radius decreases, to maintain concentricity automatically." ([284](https://developer.apple.com/videos/play/wwdc2025/284/))
  - "The closer the view is to the container's corner, the more its radius should match." ([WWDC26 289](https://developer.apple.com/videos/play/wwdc2026/289/))
- **Capsule versus rounded rectangle.**
  - "Capsules bring focus and clarity to touch-friendly layouts, but in dense desktop environments, they're best used for standout actions." (356)
  - On macOS, small controls keep rounded rectangles "for compact, high-density layouts like inspector panels" (356).
  - The default glass shape is a capsule. Use "a rounded rectangle if you're applying the effect to larger components that would look odd as a Capsule" ([Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)).
- **Why round shapes.**
  - "These clearly defined shapes feel easy to tap and are designed to relate to the natural geometry of our fingers" (219)
  - The visionOS reasoning: "People's eyes tend to be drawn toward the corners in a shape … The more rounded a button's shape, the easier it is for people to look steadily at it." ([HIG Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons))
- **Custom components in bars.** "If you need to create a custom component, ensure that its corner radius is also concentric with the bar's corners." (HIG Toolbars)
- **macOS 27 moderated the roundness.** Every window got "the same tighter corner radius" ([102](https://developer.apple.com/videos/play/wwdc2026/102/)), after critics disliked Tahoe's large radii.

---

## 3. Critique and reception

### 3.1 Legibility, the central charge

- **Nielsen Norman Group** (Raluca Budiu, 2025-10-10, [NN/g](https://www.nngroup.com/articles/liquid-glass/)):
  - "iOS 26's visual language obscures content instead of letting it take the spotlight."
  - "One of the oldest findings in usability is that anything placed on top of something else becomes harder to see."
  - "Overall, Apple is prioritizing spectacle over usability"
- **Fast Company** (Mark Wilson, 2025-09-18; read via the [Fast Company Middle East syndication](https://fastcompanyme.com/technology/apples-liquid-glass-the-liquid-works-but-the-glass-is-broken/)):
  - "Glass's fatal flaw is the clarity with which it depicts information."
  - Jakob Nielsen: "low-vision users and people with various forms of slight cognitive impairments... will suffer."
  - On Apple's opacity fixes: "The fix negates the most egregious issues. It also negates the core concept behind Liquid Glass."
- **Nick Heer** ([Pixel Envy](https://pxlnv.com/blog/on-liquid-glass/)):
  - "the impression of translucency is usually at odds with legibility"
  - "Clarity and structure are sacrificed for the illusion of simplicity offered by a monochromatic haze of an interface."
  - On glass that flips between light and dark: "Apple's clever solution to a problem Apple created."
- **Louie Mantia** ([Mastodon](https://pdx.social/@louie/114760076589198466)): "Apple has to intentionally put content out of focus (blurring) to make the glass elements visible."
- **Marco Arment** ([Mastodon](https://mastodon.social/@marcoarment/114778761310429014)): "Text on my phone should never be blurry."
- **Ryan Thomson** ([2026-06-07](https://www.ryanthomson.net/articles/liquid-glass-one-year-later)): over plain backgrounds "you end up with a lot of unpleasant grey-on-grey."
- **Apple's answer in iOS 26.1** was a Clear/Tinted setting: "Tinted increases opacity and adds more contrast." ([9to5Mac](https://9to5mac.com/2025/10/20/ios-26-1-beta-4-adds-new-setting-to-tone-down-liquid-glass-transparency/))
  - Gruber: "there should have been no need for the 'clear/tinted' Liquid Glass preference setting" ([Bad Dye Job](https://daringfireball.net/2025/12/bad_dye_job))

### 3.2 Glass everywhere, spectacle and motion fatigue

- **Dan Moren** ([Six Colors](https://sixcolors.com/post/2025/09/ios-26-review-through-a-glass-liquidly/); the review is Moren's, not Jason Snell's):
  - He questions whether "having a transparent button sitting right on top of your email is helping that email be more prominent."
  - "after the fifteenth time, the animations are less novel and more distracting."
- **NN/g:** "delight turns into distraction on the tenth, twentieth, or hundredth time."
- **Jesper** ([take.surf](https://take.surf/2025/06/30/busy-dye-ing)): "effects that are technically impressive but not in the apparent service of any particular goal."
- **CNN's team**, speaking at an Apple-hosted showcase ([Meet with Apple 256](https://developer.apple.com/videos/play/meet-with-apple/256/)):
  - "Applying the glass effect to both a parent and child views led to visual redundancy. Double translucency, layered blur, and unpredictable rendering."
  - Their rule: glass for "static or top level components like the tab bar and toolbars", not high-frequency areas.

### 3.3 Whether it fits the Mac

- **Heer:** "Liquid Glass feels suited to a whole-screen-app touch-based context. In MacOS, it feels alien" ([Pixel Envy](https://pxlnv.com/blog/on-liquid-glass/)).
- **Thomson:** "Add in windowing, multiple scrolling views, or a sidebar, and the whole thing starts to fall apart." ([ryanthomson.net](https://www.ryanthomson.net/articles/liquid-glass-one-year-later))
- **Gruber:** "I actually think, on the whole, iOS 26 is a better and more usable UI than iOS 18 … But MacOS 26 Tahoe is a mess, visually" ([Bad Dye Job](https://daringfireball.net/2025/12/bad_dye_job))

### 3.4 Critiques of specific patterns

- **Collapsing navigation** (NN/g): "users now have to play hide-and-seek with the navigation controls."
- **Content under sidebars** (Heer): "*why would you want stuff under the sidebar*?"
- **Icons in every menu item** (Nikita Prokopov, 2026-01-05, [tonsky.me](https://tonsky.me/blog/tahoe-icons/)): "if everything has an icon, nothing stands out."
  - macOS 27 now hides menu icons by default.
- **Glass highlights on icons** (Michael Flarup, [newsletter](https://www.flarup.email/p/through-the-liquid-glass)): the uniform highlight "reduces contrast and muddies detail" on light backgrounds.
- **Glass layered over flat design** (Heer): it "looks out of place when it is used in apps that rely on layouts driven by simple shapes and clean lines."

### 3.5 What critics praise

- **The motion works.** Wilson praises "some truly gorgeous animation work"; the article's title is "The liquid works, but the glass is broken."
- **Heer:**
  - "a very cool feeling of true dimensionality"
  - The morphing helps "justify the 'liquid' part of the name"
  - Floating controls work better "because the controls have this glassy quality."
- **Thomson:**
  - "Liquid Glass looks great when it's layered over media, like a photo gallery."
  - "animation in general is a major high point of this release."
- **Moren:** direct touch "makes the feel responsive and more like physical things that you're interacting with."
- **Marques Brownlee** ([transcript](https://rosetta.to/u/mkbhd/ios-26-hands-on-liquid-glass)): "My favorite part of this new design is definitely the lock screen"
- **Tim Schmitz** ([Mastodon](https://mastodon.social/@Timschmitz/115175024644773675)): "Buttons that look like buttons … are a huge improvement."
- **Roger Wong** ([2025-10-14](https://rogerwong.me/2025/10/liquid-glass-is-cracked-and-usability-suffers-in-ios-26)): flat, static UI "can get boring and homogenous quickly."

### 3.6 The ambition critique

- **Gruber, September 2026** ([AppZapper 3000, footnote](https://daringfireball.net/2026/09/appzapper_3000)):
  - "the real problem with Liquid Glass is the lack of ambition. … It aspires only to see-through blandness."
  - "The whole point is for the application chrome to defer to 'content' … which necessarily results in applications that look shy. They all look alike."
  - This is the strongest argument that deference, pushed to the limit, erases character.

### 3.7 Reception of the 27 refinements

Michael Tsai's roundup ([mjtsai.com, 2026-06-09](https://mjtsai.com/blog/2026/06/09/liquid-glass-27-slider/)):
- Tsai: "It's definitely improved. I'm not sure it's better than pre–Liquid Glass"
- Kyle Howells: "Adding UI sliders like this isn't design."
- Riccardo Mori: "We improved Liquid Glass by letting you reduce the effects until there's no more Liquid Glass"
- Jesper: "iOS 27 still suffers from the basic usability issues"

---

## 4. Lineage and vocabulary

### Apple's own framing

- "It builds on learnings from all the way from the Aqua user interface of Mac OS X, through to the realtime blurs of iOS 7, to the fluidity of iPhone X, the flexibility of the Dynamic Island, and the immersive interface of visionOS." ([219](https://developer.apple.com/videos/play/wwdc2025/219/))
- Newsroom: "Inspired by the depth and dimensionality of visionOS"
- Keynote, as transcribed by Gruber: "Inspired by the physicality and richness of VisionOS" ([Daring Fireball, 2025-06](https://daringfireball.net/2025/06/some_brief_thoughts_and_observations_on_wwdc_2025))
- Dye, as quoted by Thomson: "we challenged ourselves to make something purely digital feel natural and alive."

### Aqua (2000/2001)

- Jobs, quoted by Gruber: "we call that new user interface Aqua, because it's liquid. One of the design goals was when you saw it, you wanted to lick it."
- Gruber: Liquid Glass "is very reminiscent of Aqua a quarter century (!) ago."
- Mantia: "one could say Liquid Glass is like a new version of Aqua." ([lmnt.me](https://lmnt.me/blog/rose-gold-tinted-liquid-glasses.html))
- Heer: Aqua "at least felt like a complete idea."
- Steve Troughton-Smith, on the 27 look: "Tell me that's not Aqua" ([via Tsai](https://mjtsai.com/blog/2026/06/09/liquid-glass-27-slider/))

### iOS 7 (2013)

- The 2013 press release introduced "distinct, functional layers" and said "the use of translucency and motion makes even simple tasks more engaging." ([Apple Newsroom 2013](https://www.apple.com/newsroom/2013/06/10Apple-Unveils-iOS-7/))
- The principles were clarity, deference and depth. Apple evangelist Mike Stern's tests for deference were "Is the interface calling attention to itself?" and "Does the interface compete with content?"
- He also warned: "Other uses of blurring and translucency really, again, are just there for eye candy." ([iOS 7 Tech Talk index](https://nonstrict.eu/wwdcindex/tech-talks/2013-12/))
- Liquid Glass's "deferring to the content" is the deference principle again, now expressed optically.

### visionOS (2023), where the discipline comes from

All from [WWDC23 10076](https://developer.apple.com/videos/play/wwdc2023/10076/):
- "Avoid using solid colors on windows. Too many opaque windows can feel constricting"
- "Try to not stack lighter materials on top of each other, as it impacts legibility and reduces contrast." This is the forerunner of "no glass on glass."
- "Vibrancy … works by pulling light and color forward from what's behind it."
- Colin Cornaby's counterpoint ([Mastodon](https://mastodon.social/@colincornaby/114898632851931183)): Apple "picked an entirely different glass material than visionOS where this is working well."

### Practitioner vocabulary

- **Physicality / "new skeuomorphism"** (Sebastiaan de With, 2025-06-03, [Lux](https://www.lux.camera/physicality-the-new-age-of-ui/)):
  - "We've come back, in a sense, to skeuomorphic interfaces — but this time not with a lacquer resembling a material."
  - The goal is an interface "that matches the beautiful material properties of its devices."
  - He also urged restraint: "It can be overwhelming for all elements in the interface to have a particularly rich treatment."
  - MacRumors reported in January 2026 that de With joined Apple's Human Interface team (headline only; the article was not fetched).
- **Materiality** (Paolo Ciuccarelli, Northeastern, [2025-10-09](https://news.northeastern.edu/2025/10/09/liquid-glass-texture-flat-design-apple-tech)):
  - "It's good on one side that we go back to some level of materiality."
  - "I don't want to see animations and interactions that don't really enable something that wasn't possible before"
- **Honest depth** (Roman Kamushken, [Setproduct, 2026-06-09](https://www.setproduct.com/blog/liquid-glass-vs-glassmorphism)):
  - "depth always comes back, but only the honest versions stay"
  - "Skeuomorphism died because its depth was fake decoration. Neumorphism died faster because its depth erased contrast."
  - "Always design the solid-color version first, then layer glass on top."
  - "Where glassmorphism blurs the background, liquid glass bends it"
- **"Optical integrity" rather than "optical honesty".** Apple's own nearest phrase is materializing in a way "that preserves the optical integrity of the material" (219). No source was found that uses "optical honesty" as a term.

---

## 5. Motion

- **Look and motion were designed together.**
  - "both the visuals AND motion of LiquidGlass were designed as one." (219)
  - "Liquid Glass responds to interaction by instantly flexing and energizing with light."
  - "an inherent gel-like flexibility to it that communicates its transient and malleable nature, as it moves in tandem with your interaction." (219)
- **Feedback comes from inside the material.**
  - "the material illuminates from within as a form of feedback."
  - The glow "spreads throughout the element and onto any Liquid Glass elements nearby" (219).
  - "Glass reacts to user interaction by scaling, bouncing, and shimmering" ([323](https://developer.apple.com/videos/play/wwdc2025/323/))
- **Morphing keeps continuity.**
  - "Liquid Glass dynamically morphs between the controls in each context. This maintains the concept of having a singular floating plane" (219)
  - "When a presentation … is originated from a glass button, the button morphs into the overlay." ([284](https://developer.apple.com/videos/play/wwdc2025/284/))
  - Nearby shapes "start merging like small droplets of water." (284)
  - Morphing and materialize transitions should look "purposeful" and be used consistently ([Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)).
- **Appear by materializing, not fading.**
  - "Instead of fading, Liquid Glass objects materialize in and out by gradually modulating the light bending and lensing" (219)
  - "prefer setting the effect property over the alpha" (284)
- **Motion scales with the input method.** "the movement of Liquid Glass responds to direct touch interaction with greater emphasis … but produces a more subdued effect when a person interacts using a trackpad." ([HIG Motion](https://developer.apple.com/design/human-interface-guidelines/motion))
- **macOS 27 added a click bounce**, with explicit restraint: use it on "controls and buttons, or glass containers of interactive controls … A little goes a long way!" ([WWDC26 289](https://developer.apple.com/videos/play/wwdc2026/289/))
- **Where motion should be held back** (HIG):
  - "**Add motion purposefully, supporting the experience without overshadowing it.**"
  - "**In apps, generally avoid adding motion to UI interactions that occur frequently.**"
  - Under Reduce Motion: "Tightening animation springs to reduce bounce effects" and "Avoiding animating into and out of blurs" ([HIG Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility))
- **The spring character Apple built on:**
  - WWDC18 ([803](https://developer.apple.com/videos/play/wwdc2018/803/)):
    - "we recommend starting with 100% damping, or no overshoot"
    - "if the gesture that's driving the motion itself has momentum, then you should reward that momentum with a little bit of overshoot."
    - "bounciness needs to be purposeful."
  - WWDC23 ([10158](https://developer.apple.com/videos/play/wwdc2023/10158/)):
    - "When you're not sure, use a spring with bounce 0"
    - "be cautious about using values higher than around 0.4"
- **Critics on motion:**
  - NN/g: "Motion for motion's sake is not usability. It's distraction with a side of nausea."
  - Craig Grannell ([Revert to Saved](https://reverttosaved.com/2025/07/13/accessibility-and-apple-dizziness-by-a-thousand-cuts/)): "transforming static to animated UI via refraction is a potential trigger."
  - Heer: Mac animations "would become tiresome in a matter of minutes."
  - Thomson on the character when it works: "like beads of a viscous gel sliding across a hydrophobic surface … more 'liquid' than 'glass'."

---

## Principles a guideline could teach

1. Glass is for navigation and controls only. Content, including lists, cards and backgrounds, stays out of it. [Apple-stated]
2. Keep one floating plane. Never put glass on glass; anything placed on glass uses fills or vibrancy instead. [Apple-stated]
3. Custom glass is rare. Keep it for the few most important functional elements and prefer standard components. [Apple-stated]
4. Glass needs something worth bending behind it. Over rich media it pays off; over flat, plain UI it reads as grey haze. [practitioner consensus; Apple implies it through the Clear rule and "vibrant content underneath" sidebars]
5. Design the resting state without content–glass overlap. Overlap should be something that happens briefly while scrolling. [Apple-stated]
6. Use Regular by default. Use Clear only over rich media, with bold, bright foregrounds and dimming over bright content. Never mix the two. [Apple-stated]
7. Glass has no colour of its own. Controls are monochrome by default and take colour from the content. [Apple-stated]
8. Tint means "primary". Use one prominent action (two at most), put the colour on the background rather than the label, and never use an opaque solid fill in place of tint. [Apple-stated]
9. Brand colour lives in the scrolling content layer, not in the bars. [Apple-stated]
10. Avoid similar hues in control labels and the content beneath them. [Apple-stated]
11. Build hierarchy from layout and grouping, not decoration. Group by function and frequency, use at most three groups, and never put a symbol and text in one group. [Apple-stated]
12. Use a text label whenever no symbol is unmistakable. Icons on everything make nothing stand out. [Apple-stated; reinforced by practitioners]
13. Legibility comes before translucency. Use Regular glass for text-heavy surfaces, bolder non-light weights, vibrant label colours, and the hard or automatic edge effect in dense chrome. [Apple-stated]
14. Designs must hold across the whole appearance range: ultra clear to fully tinted, Reduce Transparency, Increase Contrast, Reduce Motion, and light and dark. Design the solid version first. [Apple-stated (test); practitioner (solid first)]
15. Concentricity: inner radius equals outer radius minus padding. Watch for pinched or flared corners. [Apple-stated]
16. Use capsules for touch and for standalone or standout actions. Use rounded rectangles for dense or desktop controls and large surfaces. [Apple-stated]
17. Presentations grow out of the control that triggered them. Glass shapes merge and split as one material. [Apple-stated]
18. Glass appears and disappears by materializing (lensing in and out), not by fading its opacity. [Apple-stated]
19. Motion is how the material behaves, not decoration. It should respond instantly, be interruptible and follow the finger, with more emphasis on touch and less with a pointer. [Apple-stated]
20. Springs should start with no bounce. Add small overshoot only where a gesture carries momentum, and "a little goes a long way." [Apple-stated]
21. Hold back motion on frequent interactions. Delight turns into distraction on repetition; under Reduce Motion, drop elasticity and blur transitions. [practitioner consensus; Apple HIG agrees]
22. Depth has to carry information. Physicality is justified when it clarifies layering or feedback. [practitioner consensus]
23. Dense, pointer-driven, multi-window contexts need more structure and opacity than full-screen touch contexts. Apple's 27 changes (edge-to-edge sidebars, uniform toolbars, tighter corners) conceded this. [practitioner consensus, partly Apple-stated]
24. Floating inset chrome, content under sidebars and self-minimizing tab bars [contested]. Apple promotes them; NN/g, Heer and Thomson say they fragment navigation. The Mac rolled sidebars back.
25. Deference versus character [contested]. Apple says content should shine; Gruber says the result is "see-through blandness". The guideline must say where identity lives: content, typography, motion quality and a single accent colour.

---

## Sources not reached, or reached only second-hand

- **The Verge:** the search tool is blocked from theverge.com, so none of its pieces are cited.
- **Fast Company:** the original URL returned a 403. Quotes are from the Fast Company Middle East syndication of the same Mark Wilson article.
- **TechRadar interviews** with Dye and Federighi: the pages came back truncated. Dye's "We had to kind of treat glass very differently" and Federighi's "physical glass" line reached the agent only through search snippets and Wccftech, so they are left out of the report above.
- **iOS 7 HIG:** the Wayback Machine is blocked. The deference, clarity and depth wording is from Apple's 2013 Tech Talk transcript, via the nonstrict.eu index.
- **UX Collective** (Oleg Safranov's "materiality" essay): 403, so it is not quoted.
- **Marques Brownlee:** quoted from a third-party transcript (rosetta.to), not the video itself.
- **Figma's glass-effect material** is almost entirely about rendering parameters, which is out of scope.
