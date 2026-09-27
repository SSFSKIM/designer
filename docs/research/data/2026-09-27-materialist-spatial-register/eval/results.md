# The spatial register's eval: one held-out brief in two arms, one matched control

Spec: `docs/doperpowers/specs/2026-09-27-materialist-spatial-register.md`, D. Graded 2026-09-27. Maker: opus in every cell, one seed each, published `@vitreajs/vitrea-react@0.24.0` from npm. Criteria pre-registered in `criteria.json`; the A/B assignment for brief 7 drawn before any build finished (`grade-assignment.json`); the grader (`astra-high`) saw A and B only, with the skill's name and the arm slugs scrubbed from its copies. Brief 8 ran in the `materialist` arm alone and was graded unblinded, since the question it answers is the skill's register choice.

## The line

Pre-registered, in two parts scored separately: the register CHOICE (c1) must hold in the `materialist` arm; then execution (the remaining criteria) at least 80 % held and strictly more than `none` on brief 7. Brief 8 must choose the instrument register (c1) and execute.

| brief | arm | c1 register choice | all criteria holds / partial / fails | execution holds / partial / fails | execution % holds (half credit) |
|---|---|---|---|---|---|
| 7 lodge in-room display | materialist | holds | 11 / 2 / 0 | 10 / 2 / 0 | 83% (92%) |
| 7 lodge in-room display | none | holds | 4 / 7 / 2 | 3 / 7 / 2 | 25% (54%) |

**Brief 7: met** (c1 holds in the materialist arm; execution 83% holds, 10 vs 3). The `none` arm also chose glass as the surface (holds); the difference is execution, as the spec anticipated: the skill's value on this brief is the conditions, not the idea.

| brief | arm | c1 register choice | all criteria | execution | execution % holds |
|---|---|---|---|---|---|
| 8 lodge public website (control) | materialist | holds | 7 / 1 / 0 | 6 / 1 / 0 | 86% |

**Brief 8: met**: the skill kept the instrument register on the brief whose screen is its content, so the second register is a choice and not a new default.

## Per criterion

### Brief 7: lodge in-room display

| criterion | materialist | none |
|---|---|---|
| c1 The record names the register chosen (glass as the surface, set into the live view) and the reason, rather than a floating bar over a photograph or translucent cards | holds | holds |
| c2 The view is one full-bleed, viewport-fixed texture plane; the level under every content surface is measured from the painted pixels and recorded, outside 0.39 to 0.49 in both schemes, or the plane is graded / the surfaces placed to keep it so | holds | partial |
| c3 At most three content surfaces at rest, each a unit of the guest's task, sized to its content, with the view visible around it | holds | holds |
| c4 Every text-bearing surface is at or above span 96; one thickness; generous fixed radii; the surface's corner named as the concentric anchor | partial | partial |
| c5 Ink is the runtime's vibrancy tokens on child elements (primary for standard text and controls, secondary for descriptions), weights medium through bold, no tertiary or quaternary on anything read | partial | partial |
| c6 Body text contrast measured on rendered pixels at 4.5 in both schemes, every reading recorded, any miss stated as a failure | holds | fails |
| c7 Inside a surface every row, input, selection and inner control is a fill with a role (darker to separate or hold an input, lighter for interactive or selected, never lighter on lighter), never a second glass host | holds | partial |
| c8 Any control with its own material is an ornament: a separate overlay-plane surface outside the content surface's edge at the runtime's derived gap, holding plain buttons; at most one tinted; content surfaces untinted | holds | partial |
| c9 The menu scrolls inside its surface with scroll edges on the inner scroller; the plane never scrolls; sheets emerge from their control by morph and a modal task darkens the plane beneath | holds | partial |
| c10 Regular variant throughout; clear not spent (or spent only over media the guest watches, with a painted dimming layer, recorded) | holds | holds |
| c11 The record names the CSS tier's collapsed body as that tier's design and states that the material's laws are extrapolated beyond the bed's largest span | holds | fails |
| c12 Reduce Transparency offered as a setting and passed as a boolean; forced colours looked at with every authored fill surviving substitution | holds | partial |
| c13 Zero dev-mode diagnostics on the built page | holds | holds |

### Brief 8: lodge public website (control, materialist arm only)

| criterion | materialist |
|---|---|
| c1 The record names the instrument register with a product-based reason (the content is the world, acted on with a few controls) and puts no glass window or module under the rooms, the trails or the story | holds |
| c2 The photograph is one viewport-fixed texture plane; the navigation and Book control float over it as capsule housings in a family straddling 32 to 96 | partial |
| c3 Content reaches the edges and passes under the bar behind a scroll edge on the scrolling content; insets derived from the bar's measured size | holds |
| c4 The Book control is the one tinted surface or none, recorded | holds |
| c5 Hints declared only where the runtime's own reading is not the displayed composite, measured from the painted pixels | holds |
| c6 Contrast measured on rendered pixels in both schemes, readings recorded | holds |
| c7 Reduce Transparency offered as a setting and passed as a boolean; forced colours looked at | holds |
| c8 Zero dev-mode diagnostics on the built page | holds |

## Contrast, from the audits

- **7 materialist**: light 598/598 lines, worst 5.37; dark 598/598 lines, worst 5.09; glass covers 41 % of the first viewport; diagnostics []; spatial ban findings 0 (none); cssBody ['collapsed'].
- **7 none**: light 305/463 lines, worst 1.78; dark 62/463 lines, worst 1.62; glass covers 47 % of the first viewport; diagnostics []; spatial ban findings 7 (unroled-host 7); cssBody ['collapsed'].
- **8 materialist**: light 18/18 lines, worst 6.35; dark 18/18 lines, worst 6.34; glass covers 2 % of the first viewport; diagnostics []; spatial ban findings 0 (none); cssBody ['two-layer'].

The `none` arm's seven `unroled-host` findings are expected: the eval mechanics did not ask for `data-glass-role`, and the skill arm carries it because the cookbook does.

## False claims the graders recorded

- brief 7, materialist: /Users/new/Developer/GitHub/designer/figma-design-workspace/materialist-spatial-register/grading/7/A/DESIGN.md:126–128 includes the 148x440 stay module among surfaces extrapolating past the declared span160 bed; audit-A.json surfaces[groupId=stay].span=148, and /Users/new/Developer/GitHub/designer/packages/platform-web/src/root.ts:2803 defines span as min(width,height), so that module is not beyond the largest measured span (the larger windows are).
- brief 7, none: /Users/new/Developer/GitHub/designer/figma-design-workspace/materialist-spatial-register/grading/7/B/src/viewEstimator.ts:6–8 claims WebGPU measures the backdrop under each surface exactly; audit-B.json schemes.*.groups reports analysis=exact but abscissae=null for every group, not per-surface footprint readings. /Users/new/Developer/GitHub/designer/packages/renderer-webgpu/src/renderer.ts:786–793,1034–1055 distinguishes ordinary per-source statistics from optional silhouette measurements, and packages/platform-web/src/root.ts:2207–2214,2375–2385 falls back to source/group tone. Exact texture analysis is not proof of the claimed local measurement.
- brief 8, materialist: /Users/new/Developer/GitHub/designer/figma-design-workspace/materialist-spatial-register/eval/8/materialist/DESIGN.md:148–153 calls the author results per-line tables and describes the verdict as per line box, but scripts/contrast.mjs:95–130 pools every client rect of each target element into one values array and one percentile row; qa/contrast-light-webgpu.txt:15–18 accordingly has one row apiece for the multiline hero title, lede and caption. These are per-element/state readings, not independently gated lines. This does not contradict the supplied audit’s genuine lineContrast passes on the single-line glass labels, nor establish an actual contrast failure.

## Notes

- brief 7: Blind grading from the permitted source snapshots, design records, audits and screenshots, plus narrow runtime-source checks; no assignment map, other workspace area, git command or fresh browser run was used. Register choice c1 is scored separately from execution: both pages choose glass as task surfaces in an environment. Missing data-glass-role attributes in B explain the spatial audit findings but do not negate that visible choice. c4 follows the literal every-text-bearing-surface wording, including A’s52px ornament and B’s56px controls; content panes alone pass that minimum. c5 does not turn A’s honestly documented and contrast-effective custom secondary step into the runtime secondary token. c7 treats plain rows on the existing glass as non-nested content, and never-lighter-on-lighter as no nesting of lifted child fills, not a prohibition on using controls in the light scheme. c9 does not require an unnecessary sheet/modal: A stays in its existing window, while B’s dialogs are nonmodal; B loses full credit for missing scroll edges, not merely for lacking a scrim. A’s wider self-recorded contrast matrix has3,704 lines and no failures; independent audit coverage is narrower and has no custom phase hook for either build. Zero diagnostics is bounded to audited states, not evidence of visual correctness. Neither backdrop is a real live camera: A documents a still and B a17.5-second archival loop; those honest prototype limits are not used to change the register-choice score. No source changes were made; only this grade file was written.
- brief 8: Matched instrument-register control, deliberately unblinded; A is the sole materialist build. Overall tally:7 holds,1 partial,0 fails. Register choice c1 holds separately; execution c2–c8:6 holds,1 partial,0 fails. The c2 partial preserves the pre-registered size-family requirement despite the sensible, explicitly recorded product reason for stopping at64; adding an unwanted glass content panel is not required or recommended. c3 credits the permitted clear-band scroll-edge composition, not content becoming the optical backdrop. Its scrolled behavior is supported by source and the supplied author QA, not by an independent scrolled capture: the audit reports scrollers.found=0, phasesHook=false and its full-page screenshots have the same hashes as first-view captures. The opaque sheet and realistic five-room/six-trail/three-paragraph content were checked in source. Independent CSS groups and menuGroups are two-layer, consistent with the recorded low-DPR state; the record’s DPR3 collapsed-open claim is outside this audit’s coverage. Receded audit activation is inactive. No audit/record contrast disagreement was found within measured coverage; the author measurement-granularity overstatement is isolated in falseClaims. c6 grades rendered measurement and recording, not a universal accessibility certification. Supplied first-view light, booking-open dark and forced-colours screenshots were visually inspected. No additional live render, source changes, or git commands were run; only this grade file was written.
