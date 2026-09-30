# Parent's rulings on the G2 step 3 implementation design (67e9d784), 2026-09-30

1. Fork 1: (a) is ACCEPTED. D1 and D2 act inside the law only, as plain value drops whose identity is
   the shipped convention. This matches the rehearsal: the band's shipped share is the shipped path.
2. Fork 2: ACCEPTED. Build LT plus the declared discrete choices that need no new operator. A
   survivor that needs a new operator is built after step 2 names it.
3. Fork 3: ACCEPTED ON A CONDITION. Candidate 2's rules between spans, and for completing a sparse
   stratum, are not new choices. They must be exactly what the hashed instrument/gate uses to form
   candidate 2's native T at a given span, including the blind H prediction at s = 112. Note that
   `tone.memo_c_T` snaps to the nearest tabulated span (ties go to the first) and completes a sparse
   span as base curve + residual interpolated through its points and held beyond them. If the
   declared candidate-2 path (the gate / exposure runner / rehearsal) defines both rules, the
   runtime reproduces them and the note cites them. If it is silent on either, write a PRE-READ
   ADDENDUM now, before anyone reads family A. The addendum must:
   - have no free parameters;
   - pass through every measured ordinate;
   - be monotone, reducing to the full row where no residual exists;
   - state the s = 112 reading explicitly.
   The parent reviews it before step 2 starts. No 104 row.
4. Fork 4: ACCEPTED. The law stands down on non-regular variants. The clear variant under the law is
   a named gap.
5. Fork 5: ACCEPTED. It is `kneeForms`' own definition of the per-channel form (chroma argument
   M_rgb). The note should cite `kneeForms` as the governing text, not only the rehearsal.
6. Fork 6: ACCEPTED. E3 under the law takes the law's fold.
7. Named gaps and debt to record in the note's closing section, to be carried to the tracker at G2's
   landing:
   - a source whose level 0 is not the device grid;
   - groups sampling through `css-backdrop` on the WebGPU tier, where no pyramid exists, so the law
     cannot run there (verify this reading);
   - `landed_tone` as a duplicate, to be deduplicated after the goldens pass;
   - the clear variant.

# Adversarial review of 67e9d784 (a708a3835f2164c2a): verdict needs-attention; parent dispositions

All six findings are ACCEPTED as real. The parent verified the reasoning; the reviewer's reproductions are CPU-only.

- R1 [P1] The on-luma knee is discontinuous in the hinge decision. Half-float storage flips it near
  L(W) = L(C), and family E's isoluminant pairs sit exactly there (30.49 codes at one deep pixel).
  - Ruling: the discontinuity belongs to the declared family, and the design must say so.
  - The implementation must agree with the f64 oracle except on a set of pixels whose size is
    measured and reported. The per-channel knee is continuous; the on-luma knee is not.
  - The luma comparison therefore needs f32 precision end to end: f32 tiles (rgba32float, or an
    f32 luma companion) at least whenever `bodyLawKnee` != 0.
  - Each storage format is a measured choice: the precision proof runs RGB cells, family E
    included, under all three knees. Report each knee's flip fraction and worst error.
  - No epsilon or deadband: that would change the declared family.
- R2 [P1] A leaves union material outside every member unwritten (`geometry/src/union.ts:101-116`).
  - Ruling: initialise the whole sampleable group texture to the captured encoded backdrop, as the
    rehearsal initialises its whole canvas.
  - Overwrite each owned R_fp in full, not only within one device px of the contour.
  - Prove coverage against the real union and the bilinear support, with a close-member,
    receded, refraction-off test.
  - If the rehearsal's owner rule gives union pixels outside every R_fp the backdrop, the
    runtime does the same, and the note says so.
- R3 [P2] The error mirror does not model the planned storage graph.
  - Ruling: rebuild the mirror (U2's test 6) as the exact planned graph. Model every stored pass's
    format, the RGBA numerator and weight, the floor pass, the final A store and its bilinear read.
  - Cover the whole drawn population, including depth 20 to 20 + 16.8t, and run it through both
    implemented tones.
  - The resulting figure replaces 0.115 / 0.127 as the budget and the shader-vs-oracle tolerance.
    If it breaks the ~0.13-code target, revisit the level count and formats before U3.
- R4 [P2] The band blend space differs from the rehearsal's (`swap.py:322-337`, encoded after tint).
  - Ruling: reproduce the rehearsal: weight the two bodies' difference in encoded output codes,
    with the tint transfer applied as the rehearsal applies it.
  - A cheaper order (for example, an encoded blend before the tint) is admitted only if the CPU
    reference shows it within 0.1 code of the rehearsal on the canonical band cells, tinted ones
    included.
  - Record which was built, and why.
- R5 [P2] The CSS filter algebra is wrong: `feBlend` composites source-over on the blurs' partial
  alpha, and a clamped arithmetic primitive clips N when lambda is outside [0, 1].
  - Ruling: normalise each blur to opaque before blending (for example, an alpha table set to 1 on
    un-premultiplied values).
  - Compose M without clipping inside the admitted lambda range where the primitives allow it.
    Otherwise classify the route as an approximation, measured in Decision Log 4.
  - The engine row stays "unverified".
- R6 [P2] The tone table needs 75 floats, and 18 vec4s hold 72.
  - Ruling: use 19 vec4s, and pin the complete CPU/WGSL offset map and its final extent in a test.

# Parent's rulings on U1/U2's hand-back (000036ed, 7b42b758, 7ddd47f5), 2026-10-01

- The native-T pre-read addendum (`native-t-addendum.md`, SHA-256 23e400bf...) is ACCEPTED as
  written. The parent reviewed items 1-6 and the s = 112 statement (T = 0.5 T96 + 0.5 T128).
  - It was committed before any family-A pixel was read; the archive is unpublished.
  - Step 2 pins its hash beside the declaration's and cites it wherever native T is read.
  - Decreasing measured ordinates remain a finding for the parent.
- Level count, decimation and tolerance: ACCEPTED as follows.
  - Six levels, with `forward.py`'s own 12-device-px decimation rule. Matching the oracle's rule is
    the cleaner parity.
  - The shader-vs-oracle tolerance is 0.15 code, which is below a third of the 0.5-code repeat floor.
- Formats: ACCEPTED. Every tile and A are rgba32float, read by manual bilinear, with two targets per
  pass. The bench in G3 reads the cost. If it is prohibitive, the formats are revisited on a
  measurement, not by assumption.
- Knee 1 and the capture's source:
  - PREFER one capture path for every knee form, reading the source at its own precision rather
    than the rgba16float chain. That path takes family E from 100% flips to 3.6%, and it removes
    a lossy stage for knees 0 and 2 as well.
  - If that path is materially harder than the chain (for example, the placement mapping is not
    available to the capture pass), build the chain path for knees 0 and 2, and build the bypass
    only if step 2 selects knee 1.
  - State which was built. Knee 1's tolerance is a flip fraction plus a 0.15-code bound off the
    flips.
- The suite timeouts under the sitting's load are environmental. The full suites are re-run at
  normal load after the sitting, before any merge.
