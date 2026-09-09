# Independent review of the capsule refinement

The review found three responsive defects and one guidance ambiguity after the desktop audit:

- Park Trails: the increased planner padding overlaps the CTA at widths just above the 720px
  collapse; measured at 721px, the overlap was 11.6px.
- Music Player: at 350px the remaining-time label extended beyond the transport and was clipped.
- Transit Ops: the view stack becomes a single horizontal row below 1024px but retained the
  vertical stack's fixed rounded-rectangle geometry.
- The capsule preference needed an explicit distinction between outer floating housings and
  the compact inner controls described by the frozen QA rule 10.

A bounded fix wave addressed these. Park now collapses at 748px, Music compacts spacing through
400px, and Transit switches its view control to capsule geometry below 1024px. The runnable
`docs/research/scripts/capsule-responsive-regression.mjs` passes 123 boundary/transition states,
including repeated host release and registration. The three affected desktop audits were refreshed;
the earlier audit and hashes remain under `pre-review/`. The QA prose now distinguishes outer
housings from compact inner controls without changing the numbered baseline rubric. The original
1440px audit remains evidence for that viewport, not for these newly checked boundary states.

The separate numerical-renderer review confirmed the clamp's safety but corrected its explanation:
normalized shadow distance, spread and vertical offset were conflated in the reported depth.
That correction changes prose only and retains the original observed readings in the spec.

The independent recheck reran all 123 layout states and confirmed the three behavioral
corrections. It identified two remaining documentation contradictions: the primary park mechanics
still named the earlier collapse boundary, and the QA glossary still excluded capsule-ended
concentric children. Both documentation corrections are applied and checked against the verified implementation and
unchanged rubric digest. No additional runtime or layout change is required. The bounded review
is complete; earlier unrelated responsive debt remains recorded rather than expanding this pass.
