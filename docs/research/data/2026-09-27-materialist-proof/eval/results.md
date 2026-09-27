# The materialist against an unaided opus: six briefs, two arms, blind grading

Spec: `docs/doperpowers/specs/2026-09-27-materialist-proof.md`, C. Graded 2026-09-27. Maker: opus in both arms, one seed each. Criteria pre-registered in `criteria.json`; A/B assignment drawn before grading in `grade-assignment.json`; graders (`astra-high`, one per brief) saw A and B only. The grader was blind to the label and not to the content (a cell carrying the skill's record template is recognisable); the skill's name was scrubbed from the blind copies.

## The line

Pre-registered: the `materialist` arm holds at least 80% of the criteria on every brief and strictly more than `none` on each of 1, 2, 3, 5 and 6; on 4 it names at least four of the five faults. `holds` counts only a full hold; the figure with half credit for `partial` is beside it.

| brief | criteria | materialist holds / partial / fails | none holds / partial / fails | materialist % holds (half-credit) | none % holds (half-credit) | line |
|---|---|---|---|---|---|---|
| 1 music player (React) | 12 | 9 / 2 / 1 | 3 / 4 / 5 | 75% (83%) | 25% (42%) | NOT met: 75% holds, 9 vs 3 |
| 2 camera launch (vanilla, CDN) | 10 | 9 / 1 / 0 | 6 / 2 / 2 | 90% (95%) | 60% (70%) | met: 90% holds, 9 vs 6 |
| 3 pharmacy console (negative control) | 6 | 6 / 0 / 0 | 0 / 2 / 4 | 100% (100%) | 0% (17%) | met: 100% holds, 6 vs 0 |
| 4 component-tree review | 7 | 7 / 0 / 0 | 6 / 1 / 0 | 100% (100%) | 86% (93%) | met: names 5 of 5 faults |
| 5 weather app (React, held out) | 12 | 11 / 1 / 0 | 2 / 5 / 5 | 92% (96%) | 17% (38%) | met: 92% holds, 11 vs 2 |
| 6 architecture studio (vanilla, held out) | 12 | 10 / 2 / 0 | 5 / 2 / 5 | 83% (92%) | 42% (50%) | met: 83% holds, 10 vs 5 |

**5 of 6 briefs meet the line.**

## Per criterion

### Brief 1: music player (React)

| criterion | materialist | none |
|---|---|---|
| c1 The artwork is a registered texture plane filling the viewport edge to edge | holds | holds |
| c2 The floating inventory is short; every glass surface is a control or platter; no glass on the tracklist or queue rows | fails | fails |
| c3 Groups are planned and each declares its backdrop (texture or measured hint) | holds | holds |
| c4 A size family straddles span 32 to 96 with one thickness | holds | partial |
| c5 Capsule housings with concentric children and a named anchor | holds | partial |
| c6 The control layer is monochrome with at most one tinted primary, recorded either way | holds | fails |
| c7 The queue menu morphs from its control (GlassMorph or present), not a cross-fade | partial | partial |
| c8 colorScheme and windowActivation follow the system | partial | partial |
| c9 The app offers a reduce-transparency setting and passes a boolean | holds | fails |
| c10 Contrast is measured on rendered pixels (a measurement is recorded, not asserted) | holds | fails |
| c11 The record template is written | holds | fails |
| c12 Zero dev-mode diagnostics on the built page | holds | holds |

### Brief 2: camera launch (vanilla, CDN)

| criterion | materialist | none |
|---|---|---|
| c1 Content reaches the window's edges and passes under the bars with a scroll edge on the scrolling content, never on an ancestor of the glass root | holds | partial |
| c2 Insets are derived from the bar's measured height | holds | fails |
| c3 registerGroup uses `backdrop` (not `hint`) for the declaration | holds | holds |
| c4 The plane element's own box is what the texture is mapped onto; page paint and sampled texture agree | holds | holds |
| c5 Press is written through the channel properties, never a colour swap | holds | holds |
| c6 At most one tint, on the buy action | holds | holds |
| c7 The CSS tier is looked at and is the same design | holds | holds |
| c8 The page states that a CDN import needs network | holds | partial |
| c9 The page states that file:// boots on Chrome with a CDN URL and only a relative local module import fails | partial | fails |
| c10 Zero dev-mode diagnostics on the built page | holds | holds |

False claims about the runtime: materialist 1, none 1. materialist: /Users/new/Developer/GitHub/designer/figma-design-workspace/materialist-proof/grading/2/B/index.html:1043–1045 says texture pixels win over the declaration on WebGPU; the page supplies author backdrop hints, and /Users/new/Developer/GitHub/designer/packages/platform-web/src/root.ts:2152–2162,2211–2222 instead gives the declared luminance precedence over sampled texture tone (also marking backdropToneHint at 2304). The texture still supplies sampled imagery, but does not override that author tone declaration. none: /Users/new/Developer/GitHub/designer/figma-design-workspace/materialist-proof/grading/2/A/index.html:999–1000 says a group backdrop is fixed at registration and a change requires re-registration; this is false for the exposed scene API: /Users/new/Developer/GitHub/designer/packages/core/src/scene.ts:739–744 implements updateGlassGroup(id, patch), which can change backdrop without recreating the group.

Rendered-pixel contrast (audit): materialist: /Users/new/Developer/GitHub/designer/figma-design-workspace/materialist-proof/grading/2/B-audit.json schemes.*.glassContrast and schemes.*.schemeFollowed — light: 51/51 rendered-pixel pairs pass, minimum ratio 5.99:1; phases: fv 11/11, tile-2 11/11, tile-3 11/11, menu 18/18; root colorScheme=light, schemeFollowed=true; dark: 36/51 rendered-pixel pairs pass, minimum ratio 3.55:1; phases: fv 10/11, tile-2 9/11, tile-3 9/11, menu 8/18; root colorScheme=dark, schemeFollowed=true.; none: /Users/new/Developer/GitHub/designer/figma-design-workspace/materialist-proof/grading/2/A-audit.json schemes.*.glassContrast and schemes.*.schemeFollowed — light: 54/66 rendered-pixel pairs pass, minimum ratio 3.69:1; phases: fv 11/12, tile-2 11/12, tile-3 11/12, menu 21/30; root colorScheme=light, schemeFollowed=true; dark: 54/66 rendered-pixel pairs pass, minimum ratio 3.69:1; phases: fv 11/12, tile-2 11/12, tile-3 11/12, menu 21/30; root colorScheme=light, schemeFollowed=false.

### Brief 3: pharmacy console (negative control)

| criterion | materialist | none |
|---|---|---|
| c1 Glass is refused on cards, the table and rows (content layer) | holds | fails |
| c2 The two-layer discipline is explained in a sentence | holds | fails |
| c3 The smallest honest version is offered: an opaque tonal worksheet with at most one small persistent glass control layer, or no glass, with the tension recorded | holds | partial |
| c4 No backdrop-filter on any content surface | holds | fails |
| c5 No depicted material anywhere | holds | fails |
| c6 Density and criticality are respected in the built page | holds | partial |

False claims about the runtime: materialist 1, none 0. materialist: /Users/new/Developer/GitHub/designer/figma-design-workspace/materialist-proof/grading/3/B/NOTES.md:36–38: The promise that first-expiry-first lot cards have “Pull first” marked is not consistently true: index.html:932–941 gives any status badge precedence over that marker. In the default Heparin inspector, earliest usable lot GK7664 is marked only “Short-dated”, not “Pull first”. 

### Brief 4: component-tree review

| criterion | materialist | none |
|---|---|---|
| c1 Names glass in the content layer (the list and its items) and the diagnostics that would fire | holds | holds |
| c2 Names glass on glass (a surface toolbar around surface buttons; GlassToolbar is not a surface) | holds | holds |
| c3 Names the solid background standing in for a tint and prescribes tint with one seed per group | holds | partial |
| c4 Names that Reduce Transparency cannot be queried on every engine and that the app needs its own switch passing a boolean | holds | holds |
| c5 Names the ancestor filter that re-roots the backdrop and demotes every group with probe-failed | holds | holds |
| c6 Orders findings by severity and cites the layer model rather than taste | holds | holds |
| c7 Does not rewrite the code | holds | holds |

False claims about the runtime: materialist 5, none 3. materialist: A lines 31–32: “Every result row is a registered host that is measured every frame” is false. packages/platform-web/src/geometry-sync.ts:1–13,278–306 measures only dirty hosts and performs no host measurements at steady state. The adjacent claim that rows remount when the query changes is also not guaranteed by vitrea; React identity/keys and actual membership changes determine remounting. materialist: A lines 42–49 guarantees two errors “for each nested pair.” The diagnostic categories are right, but the structural count is not: packages/platform-web/src/layer-model.ts:135–169 returns the first nesting found and emits one glass-inside-glass report per registration. Registering an outer host after several children need not report every outer/child pair. same-plane-overlap separately checks measured visible intersections, not an unconditional registration-time pair count. none: B lines 41–44 and 65–66 guarantees glass-inside-glass for every row/button. packages/platform-web/src/layer-model.ts:135–169 finds only the first nesting and reports once per registration, so an outer host registered after multiple children need not yield one structural report per child. The named diagnostic mechanisms remain correct; the count is not guaranteed. none: B lines 73–75 says the partition gap derives from blur the runtime “actually drew.” packages/react/src/controls/toolbar.tsx:493–541 uses a conservative bound from the selected active endpoint with resolved scheme/policy and explicitly ignores window pose; it does not read the actual drawn endpoint or its final tuned blur.

### Brief 5: weather app (React, held out)

| criterion | materialist | none |
|---|---|---|
| c1 The animating composite is a canvas registered as the texture plane and re-imported per frame | holds | holds |
| c2 The floating inventory is short; no glass on the outlook or the warnings | partial | partial |
| c3 The layer control is a segmented control concentric inside a capsule housing with the anchor named | holds | partial |
| c4 A size family straddles 32 to 96 with one thickness | holds | partial |
| c5 The declared backdrop is measured at the composite's lightest and darkest phase | holds | fails |
| c6 The control layer is monochrome; the warning hue lives in the content layer; no tint on a data-dependent status (or one on the primary, recorded) | holds | fails |
| c7 The station platter arrives by GlassMorph or present, never a cross-fade | holds | fails |
| c8 colorScheme and windowActivation follow the system | holds | partial |
| c9 A reduce-transparency setting passes a boolean | holds | partial |
| c10 Contrast is measured on rendered pixels in both schemes | holds | fails |
| c11 Zero dev-mode diagnostics | holds | holds |
| c12 The record template is written | holds | fails |

False claims about the runtime: materialist 1, none 1. materialist: /Users/new/Developer/GitHub/designer/figma-design-workspace/materialist-proof/grading/5/A/src/hints.ts:4–9 and DESIGN.md:42–43 frame the declarations as CSS-tier hints with GPU reading its own pixels regardless. They are not CSS-only: /Users/new/Developer/GitHub/designer/packages/platform-web/src/root.ts:2152–2159,2304–2310 sets author-hint tone precedence and backdropToneHint, renderer-bridge.ts:328–337 forwards it to GPU, and root.ts:2439–2452 forwards hint luminance to both tiers' foreground resolution. The audit's WebGPU groups report backdropToneHint:true even while analysis='exact'; that label does not mean the hint is ignored. none: /Users/new/Developer/GitHub/designer/figma-design-workspace/materialist-proof/grading/5/B/src/components/MapHero.jsx:81–82 implies resized canvases must be re-supplied because provider extents are read at construction. Construction does read an extent, but /Users/new/Developer/GitHub/designer/packages/platform-web/src/renderer-bridge.ts:597–610 refreshes source extents before frame acquisition; resize re-registration is not required by that runtime.

Rendered-pixel contrast (audit): materialist: A-audit.json schemes.*.glassContrast (rendered-pixels): light88/88 passing, minimum10.30:1; first-view45/45 and menu43/43. Dark71/88 passing, minimum3.91:1; first-view29/45 and menu42/43. Root follows both schemes (light=true, dark=true). Dark failures concentrate in the station reading (e.g. Wind4.46:1, falling fast4.31:1); the audit is a moment on an animated backdrop, not a full-loop worst-case. DESIGN.md reports better multi-frame readings, so its blanket sampled WebGPU-pass claim is not confirmed by this independent sample.; none: B-audit.json schemes.*.glassContrast (rendered-pixels): emulated light12/197 passing, minimum2.11:1; first-view6/93 and menu6/104. Emulated dark12/197 passing, minimum2.12:1; first-view6/93 and menu6/104. Actual root is dark in both: scheme-following light=false, dark=true. These are two emulation samples of the pinned dark design, not validation of a real light scheme. Failures are widespread in both phases, rather than one isolated animation-frame miss.

### Brief 6: architecture studio (vanilla, held out)

| criterion | materialist | none |
|---|---|---|
| c1 A light plane is tried first and the page is designed opaque before the glass finds the controls (visible in the record) | holds | holds |
| c2 Content reaches the edges and passes under the bar with a scroll edge on the scrolling content, never on an ancestor of the root | holds | partial |
| c3 Insets derived from the bar's measured height | holds | fails |
| c4 registerGroup declares `backdrop` (not `hint`) with a luminance measured off the photograph | holds | partial |
| c5 The texture is mapped onto the <img>'s own box, not the viewport | holds | holds |
| c6 Nav and enquiry are capsule housings; the enquiry is the one tinted control or none, recorded | holds | holds |
| c7 No glass on the project grid, the practice text or the people | holds | holds |
| c8 Press through the channel properties | holds | fails |
| c9 The CSS tier looked at and the same design | holds | fails |
| c10 The page states the CDN network need and the file:// truth | partial | fails |
| c11 The record template is written in the file's header | partial | fails |
| c12 Zero dev-mode diagnostics | holds | holds |

False claims about the runtime: materialist 1, none 0. materialist: /Users/new/Developer/GitHub/designer/figma-design-workspace/materialist-proof/grading/6/A/index.html:949-953 claims the declared luminances are the CSS tier's only knowledge and that on the GPU texture path "the pixels win". This is false: author luminance takes precedence on both tiers; the GPU silhouette reduction is used only when declaredLuminance is absent (/Users/new/Developer/GitHub/designer/packages/platform-web/src/root.ts:2360-2385), and CSS can also derive tone from a supplied texture (/Users/new/Developer/GitHub/designer/packages/platform-web/src/backdrop-tone.ts:13-22). 

## Reading

Five of six briefs meet the pre-registered line; the skill-aided arm holds more criteria than the
unaided arm on every built brief and names every fault on the review brief. The unaided arm is not
weak: on the camera page and the architecture page it put glass only on navigation and one action,
and on the review it named nine problems from the library source alone. What separates the arms is
the declaration and the record: measured backdrops, insets from a measured bar, `backdrop` not
`hint`, the CSS tier looked at, the network and `file://` truths stated, contrast measured on
rendered pixels, and on the negative control the refusal itself (the unaided arm frosted the
cards, the table and the sidebar as asked; the skill-aided arm printed the ledger opaque and floated
one command bar, and told the client why).

**Brief 1 misses the line at 75% holds.** It fails `c2` (the queue is content on glass) and `c8`
(the colour scheme is pinned). Both arms fail `c2`, and the section that should have carried the
difference is `skills/materialist/references/examples.md`, whose music-player derivation taught a
glass queue against the skill's own layer law; the six demo builds hit the same defect and the
skill's fix wave rewrites that example. `c8` follows from it: the maker pinned light because the
dark material failed contrast on the queue, a surface that should not have been glass.

**Two findings about the skill, from the skill-aided cells.** (1) Three of them repeat the
cookbook's inverted claim that texture pixels override a declared hint (`vitrea.md` §2); the runtime
does the opposite, and the skill's fix wave corrects it. (2) Following the system colour scheme
costs contrast the unaided arm avoided by pinning light: the skill-aided camera page passes 51/51
glass text pairs in light and 36/51 in dark (min 3.55), the weather page 88/88 and 71/88 (min
3.91). The dark material over a bright photograph lands labels below 4.5:1 unless the page grades
the plane or authors its ink; the skill says both are allowed, and the eval says makers do not
reach for them without being told when.

**Limits.** One seed per cell, one grader per brief, blind to the label and not to the content.
The rendered-pixel contrast sample on an animating plane (brief 5) is a moment's reading. The four
registered briefs are within reach of the skill's worked examples; the two held-out briefs (5 and
6) show the largest and the third-largest separations, so the effect is not retrieval of an example.
