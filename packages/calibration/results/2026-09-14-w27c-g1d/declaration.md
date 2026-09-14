# W27c G1d declaration — native anchor and one frozen refit

Declared 2026-09-14 before any scene, profile, fixture, material, matrix, or harness script moves.
Authority: W27 Decision Logs 18 and 19; claims §5.141 §§3–4; contract X8. The result will be
recorded as claims §5.143. Decision Log 13's probe bar stands: no inactive floor is adopted.

## Native anchor capture

The new backdrop is `mid-light-solid`, a uniform neutral sRGB (140, 140, 140) patch (encoded
0.5490196). It occupies the widest gap in the existing uniform dark-response bed, between
`mid-dark-solid` (encoded 0.2706) and `light-solid` (encoded 0.9504), and changes neither chroma nor
structure while moving the abscissa.

The only captured scene ids are:

- `mid-light-solid__capsule-button__inactive`
- `mid-light-solid__rrect-sm__inactive`
- `mid-light-solid__rrect-ml__inactive`
- `mid-light-solid__rrect-lg__inactive`

They are declared in `apple-macos-26.5-1x-dark-standard` and
`apple-macos-26.5-2x-dark-standard`, and in `split.probe`. One pass is taken at each scale in the
inactive pose, standard accessibility only, with seven independent runs per pass. Every pass uses
the unchanged granted bundle, `VITREA_SCENES` pointed at this worktree's amended canonical
`scenes.json`, `VITREA_BED_FILE` containing exactly the four ids, and a fresh sitting root under
`$HOME`. A `DRY=1` presentation runs first at each scale and must report exactly four cells.

A pass is refused if any of these conditions fails: macOS is not 26.5.x; either
`increaseContrast` or `reduceTransparency` is not 0 immediately before the pass; BetterDisplay's
`가상 16:9` display is not id `7709FD0F-F423-4277-B0C8-7CA94F85723A` in mode 68 at 2x or mode 69
at 1x; the screen is locked; a browser, web capture, comparison, or another harness is sharing the
GPU; the dry count is not four; the harness resolves any other scene; the opening idle gate does
not reach 45 seconds; a run does not write all four fixtures; any fixture is nondeterministic,
material-free, or does not attest `presentedActive: false`, `observedPose: inactive`,
`isKeyWindow: false`, and `appIsActive: false`; or the run audit quarantines it. A refusal is kept
and reported; it is not worked around by rebuilding the granted bundle, changing the display, or
synthesising input.

Each pass is launched detached through the existing `nohup` + pid/log + `caffeinate` pattern. No
browser suite or web capture runs during it, and no UI scripting or synthetic input is used. Mode
68 (2x) is restored when the sitting ends.

Publication is one `materialize` invocation per scale over the seven run roots, with `--set probe
--frequency-settle --apply`. `manifest-doctor` runs before and after. Before publication, the
committed manifest and every tracked fixture PNG are hashed against the declaration head; after
publication, every pre-existing manifest entry and tracked PNG is compared byte-for-byte against
that same head. Publication refuses if any pre-existing entry or PNG moved, disappeared, or if the
new eight profile/scene entries are not the seven-run pluralities. The evidence records each run's
four-of-four attestation, `hidIdleSeconds`, manifest SHA-256, plurality tally, both doctor outputs,
and the sitting state. Raw runs remain only on this machine.

## Frozen fit partition

All fitting uses WebGPU. CSS is derived from the same resolved profile, measured for coherence, and
gates nothing (X1). Native-only body readings of all eight new cells are made first; no web capture
or fit is made before that reading answers the form question.

### T1 — dark response, with the new anchor

The form decision is made from the native dark-standard rows at both scales:

- **abscissa:** the uniform thin row rises materially at encoded 0.549 between its low uniform
  readings at 0.2706 and its 0.93261 reading at 0.9504;
- **structure:** the new uniform thin row remains on the low row while the far uniform cell alone
  rises, or the result otherwise leaves uniform versus structured backdrop as the explanatory
  variable.

If the answer is structure, T1 stops without a fit and records the contradiction of W9's
structure-independence premise. If it is abscissa, the additive four-knot form is swept. Existing
three-knot documents must resolve byte-for-byte to their present material SHA, and all renderer
goldens must remain byte-identical; either moving is a stop.

- **Fit:** both dark-standard scales of `mid-light-solid__rrect-sm__inactive` identify the new thin
  ordinate at zero thickness; both scales of `light-solid__rrect-sm__inactive` identify the thin
  far ordinate. If supported, both scales of `light-solid__rrect-lg__inactive` identify the dark
  thick far ordinate in the same sweep.
- **Check/refusal:** both scales of the lower uniform thin anchors
  (`dark-solid__rrect-sm__inactive`, `mid-dark-solid__rrect-sm__inactive`); the structured bright
  controls (`hc-text__rrect-sm__inactive`, `checkerboard-lc16__capsule-button__inactive`, and the
  recovered checkerboard/photo thin cells used by §5.141); and the new
  `mid-light-solid__rrect-lg__inactive`. A rung is refused rather than compromised if any declared
  control exceeds §5.141's cap of 9× its frozen G1c body-ΔE baseline or if a lower uniform anchor
  moves away from its native row.
- **Holdout:** both dark-standard scales of `mid-light-solid__capsule-button__inactive` and
  `mid-light-solid__rrect-ml__inactive`. These test thin/thick mixing and the thick continuation on
  the new backdrop. Their WebGPU-against-native result is read exactly once after T1 and the
  accessibility constants are both frozen.

### T2 — accessibility occlusion level per policy

The light receded profile gains separate Reduce Transparency and Increase Contrast levels, with
its existing shared `increasedOcclusionLift` value as the additive default. Existing documents that
name only the shared value must resolve exactly as they do at this declaration.

- **Fit (banked supplying cells):** for each policy,
  `checkerboard__rrect-md__inactive` and `photo__rrect-md__inactive`, the two calibration fixtures
  that supplied §5.141's backdrop-independence finding. The per-policy level minimises equal-cell
  mean body ΔE on only those two cells.
- **Check/refusal:** for each policy, `dark-solid__rrect-48__inactive`,
  `dark-solid__rrect-80__inactive`, `hc-text-28__rrect-md__inactive`, and
  `light-solid__rrect-ml__inactive`. They check the thin end, span independence, structured
  residual, and bright end; none is minimised over.
- **Holdout:** for each policy, `hc-text__capsule-button__inactive` and
  `photo__rrect-lg__inactive`, the profile's declared holdout fixtures. Their WebGPU-against-native
  result is read exactly once with T1's holdout after both fits are frozen. No constant moves after
  that read.

The final frozen configuration is read once against the whole checking bed. The three clauses of
§5.134 §6 are re-applied once, unchanged, to all six profiles; no floor is adopted. One native-
beside-WebGPU sheet per profile and CSS coherence evidence are produced from that same
configuration. Differences visible to the eye are recorded even where the numerical bound holds.
