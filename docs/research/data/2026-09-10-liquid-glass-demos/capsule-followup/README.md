# Capsule refinement verification

The user preferred active curvature and more capsules after viewing the baseline demos, naming
music-player and park-trails most convincing. This refinement changes control shapes and related
inner padding/radii, not the material profile, imagery, overall layouts or animation system.

All six final desktop audit runs passed at 1440×900. They recorded no page errors, console errors,
failed requests, resting diagnostics or new menu diagnostics. Every sampled contrast pair passed
in the authored appearance; this does not establish both appearances or full accessibility.
The reduced-transparency override was honoured and changed the material in each smoke check.

Each `<slug>.json` is the follow-up audit, separate from `../audit/`, which belongs to the original
panel. Captures came from copied HTML and shared image assets under
`figma-design-workspace/capsule-final-audit/`; `manifest.json` pins source and capture hashes.
The individual check notes record browser interactions and responsive observations. Music and photo
were checked at 800px; the other pages at 390px. They are not a cross-engine conformance suite.

Known earlier issues remain: the photo adjustment dock is crowded at 800px; film-festival has
resize-time overlap diagnostics and a layout problem near its existing 1080px breakpoint.
The park-trails CTA host-handle failure on repeated responsive transitions was fixed and checked
through two round trips. None of these observations alter the frozen panel ratings.

The user subsequently confirmed: "Yeah, I can confirm it's much better With more curvature".
This endorses the refinement direction; it is not converted into unprovided rubric answers.

Independent review found boundary regressions beyond the initial viewport checks. Those are now
fixed and covered by `docs/research/scripts/capsule-responsive-regression.mjs`; its passing output
is in `responsive-regression.txt`. The per-page audit and manifest above use the latest verified
HTML; earlier records are retained in `pre-review/`. See `review.md` for the findings and fixes.
