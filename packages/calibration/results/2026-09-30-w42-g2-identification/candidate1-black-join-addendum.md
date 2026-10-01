# W42 G2 — pre-read addendum: candidate 1's landed tone inside W36's open interval below the black join (2026-10-01)

**Status: the parent's pre-read amendment.** The parent's ruling is kept verbatim in
`implementation-design-rulings.md`, under "Parent's ruling on the landed solve below the black
join". This addendum is committed on its own and before G2 step 2 reads any family-A pixel.
Step 2 pins its SHA-256 beside the declaration's and beside `native-t-addendum.md`'s.

The addendum adds no family, no leaf, no parameter and no bed cell. It changes one construction:
candidate 1's per-pixel landed tone (declaration `candidate1`; the rehearsal's `landed_T`,
`gate/rehearsal/body.py:504`), and only inside an interval that W36 recorded as unidentified
(claims §5.179–§5.180).

## 1. The interval, and its end

W36's black branch acts on the solve's own abscissa, the encoded input `x = enc(level)`:
- in the rehearsal, `body.py:368`;
- in the shipped shader, `wgsl/optics.ts:1455`, `let encodedInput = srgb_encode(toneColour.w)`.

`level` is the tone abscissa:
- **source** (the active documents): the linear luminance of the backdrop, which for a per-pixel
  argument A is L_lin(dec A);
- **silhouette** (the receded documents): dec of the encoded luma, so x = L_enc(A).

The branch blends toward its black ordinates with weight strength · (1 − smoothstep(0, 0.003, x))
for x < 0.003, and 0 above. So its end, where the weight reaches 0 and the response is exactly the
old solve, is

    X_END = 0.003 (encoded input; 0.765 code)

Source lines, one per copy:
- `gate/rehearsal/body.py:373`: `bw = np.where(x < 0.003, min(max(e['black'][0], 0), 1) * (1 - smoothstep(0.0, 0.003, x)), 0.0)`;
- `packages/renderer-webgpu/src/wgsl/optics.ts:1462–1464`:
  `if (ou.toneBlack.x > 0.0 && encodedInput < 0.003) { blackWeight = … (1.0 - smoothstep(0.0, 0.003, encodedInput));`;
- `packages/renderer-webgpu/src/material.ts:4619`: `export const BACKDROP_TONE_BLACK_JOIN = 0.003;`, read by
  `backdropToneBlackWeight` at `4622–4625`.

The end lies below the lowest packed impulse input, 0.00319488975 (W36). The open interval
0 < x < X_END therefore holds no measured input. Its values are the blend of the black branch's
authority into the old solve's, which is an interpolation device and not a reading.

## 2. The amendment

Inside the open interval only, where the black branch's strength is above 0, candidate 1's
per-pixel landed tone is the straight line in the branch's abscissa between the solve's value at
0 and its value at the end, per channel:

    y(A) = (1 − x/X_END) · y(0) + (x/X_END) · y(A_end),    0 < x = X(A) < X_END

- **y** is the landed tone as declared (`landed_T`), in its own output space, linear light. So the
  line is taken in linear light, the space the tone returns and the space the renderer mixes a
  fractional tone in.
- **y(0)** is its value at black, the only argument whose abscissa is 0.
- **A_end** is A's own ray through black, carried to the end in the abscissa's own space:
  - silhouette (encoded): A_end = A · X_END / L_enc(A);
  - source (linear light): dec(A_end) = dec(A) · dec(X_END) / L_lin(dec A).

  In both cases X(A_end) = X_END exactly. For a grey argument, A_end is the grey at the end.

Everywhere else the landed tone is the solve's, unchanged: at x = 0, at x ≥ X_END, and wherever
the branch's strength is 0 (the frozen macOS 26.5 documents, where the interval does not exist).

**Properties.**
- The amendment has no free parameter.
- It is continuous at both ends: y → y(0) as x → 0, and A_end → A as x → X_END.
- Each channel lies between its values at 0 and at the end.
- At every measured input, black itself and every input at or above the lowest packed impulse
  input, it is identical to the shipped solve.
- The group-level solve is untouched, and no document leaf is added or moved, so no digest moves.

**What it does not touch.** The response above the end is the old solve in measured territory,
and it keeps its dip. The table below shows it: on receded dark it falls from 36.2 codes at code
0.8 to 0.7 at code 1.0, against a native black of 20. That dip is the existing named black-level
miss. The rehearsal's `mono_black`, which held black flat up to where the response climbs back,
stays declined.

## 3. The endpoints of the bridge

Grey output codes, every channel equal (the macOS 27 tints are neutral), from the hashed
`landed_T` on each component's own pixels.

| endpoint | component (sizeK) | y(0) | y(end) |
| --- | --- | --- | --- |
| light active | capsule (0.0923) | 132.000 | 157.312 |
| light active | rrect-sm (0) | 0.000 | 156.979 |
| light active | rrect-md, -ml, -lg (1) | 132.000 | 162.659 |
| light receded | capsule (0.0923) | 133.000 | 151.873 |
| light receded | rrect-sm (0) | 0.000 | 151.652 |
| light receded | rrect-md, -ml, -lg (1) | 133.000 | 152.368 |
| dark active | capsule (0.0923) | 32.000 | 56.672 |
| dark active | rrect-sm (0) | 0.000 | 56.707 |
| dark active | rrect-md, -ml, -lg (1) | 32.000 | 54.949 |
| dark receded | capsule (0.0923) | 20.000 | 41.105 |
| dark receded | rrect-sm (0) | 0.000 | 41.092 |
| dark receded | rrect-md, -ml, -lg (1) | 20.000 | 41.233 |

**The two scales read identically**: the rehearsal's landed solve depends on the scale only
through sizeK, which is the same per component at 1x and 2x (`implementation-design/candidate1_black_join.txt`
computes both).

**rrect-sm's y(0) of 0 is the solve as it stands, and not the black branch.** At sizeK 0 and level
0, W7's tone adaptation (low 0, high 0.0001 linear, size bias 0.05 × sizeK) is fully collapsed
(toneAdapt 1). The solve does not run, and the body is the backdrop's own black. Once sizeK
reaches 0.002 (0.0001 / 0.05), the bias lifts black clear of that window; the canonical sizeKs
are 0, 0.0923 and 1. At sizeK 0 the window ends at linear 0.0001, encoded 0.0013 (0.33 code),
which is inside the interval. The amendment reads the solve's value at 0 as
it is and does not repair it.

## 4. Before and after, over [0, 2] codes of grey input

Output codes at 1x; 2x is asserted equal. "Before" is the declared `landed_T`; "after" is the
amended one. Columns are the input in codes.

| endpoint, component | | 0.0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 | 1.0 | 1.2 | 1.5 | 2.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| light active, capsule | before | 132.0 | 134.6 | 141.3 | 150.3 | 159.8 | 168.7 | 172.5 | 166.1 | 151.8 | 136.8 | 128.0 | 127.8 | 128.0 | 128.4 |
| | after | 132.0 | 135.7 | 139.2 | 142.6 | 145.9 | 149.2 | 152.3 | 155.4 | 151.8 | 136.8 | 128.0 | 127.8 | 128.0 | 128.4 |
| light active, rrect-md | before | 132.0 | 135.2 | 143.2 | 153.4 | 163.9 | 173.1 | 177.0 | 170.9 | 157.5 | 143.4 | 135.2 | 135.0 | 135.2 | 135.5 |
| | after | 132.0 | 136.5 | 140.8 | 145.0 | 149.0 | 152.9 | 156.7 | 160.3 | 157.5 | 143.4 | 135.2 | 135.0 | 135.2 | 135.5 |
| light receded, capsule | before | 133.0 | 134.9 | 140.2 | 148.1 | 157.4 | 166.8 | 170.9 | 162.8 | 144.9 | 125.3 | 113.1 | 113.0 | 113.4 | 114.1 |
| | after | 133.0 | 135.7 | 138.3 | 140.8 | 143.3 | 145.7 | 148.1 | 150.4 | 144.9 | 125.3 | 113.1 | 113.0 | 113.4 | 114.1 |
| light receded, rrect-md | before | 133.0 | 135.0 | 140.6 | 148.9 | 159.1 | 169.4 | 174.0 | 164.9 | 144.4 | 121.3 | 106.6 | 106.3 | 106.9 | 107.8 |
| | after | 133.0 | 135.7 | 138.4 | 141.0 | 143.5 | 146.0 | 148.5 | 150.8 | 144.4 | 121.3 | 106.6 | 106.3 | 106.9 | 107.8 |
| dark active, capsule | before | 32.0 | 35.0 | 41.5 | 48.1 | 53.4 | 57.0 | 58.3 | 57.7 | 56.0 | 54.2 | 53.3 | 53.2 | 53.3 | 53.4 |
| | after | 32.0 | 36.2 | 40.0 | 43.5 | 46.7 | 49.6 | 52.4 | 55.0 | 56.0 | 54.2 | 53.3 | 53.2 | 53.3 | 53.4 |
| dark active, rrect-md | before | 32.0 | 34.8 | 40.8 | 47.2 | 52.5 | 56.4 | 57.9 | 56.7 | 53.8 | 50.9 | 49.3 | 49.3 | 49.3 | 49.4 |
| | after | 32.0 | 35.9 | 39.4 | 42.6 | 45.6 | 48.3 | 50.9 | 53.4 | 53.8 | 50.9 | 49.3 | 49.3 | 49.3 | 49.4 |
| dark receded, capsule | before | 20.0 | 22.8 | 29.1 | 36.7 | 44.1 | 50.7 | 53.4 | 48.4 | 36.1 | 18.4 | 0.7 | 0.4 | 1.1 | 2.2 |
| | after | 20.0 | 23.8 | 27.0 | 30.0 | 32.7 | 35.2 | 37.5 | 39.7 | 36.1 | 18.4 | 0.7 | 0.4 | 1.1 | 2.2 |
| dark receded, rrect-md | before | 20.0 | 22.8 | 29.2 | 36.8 | 44.2 | 50.9 | 53.6 | 48.6 | 36.2 | 18.5 | 0.7 | 0.3 | 0.9 | 1.8 |
| | after | 20.0 | 23.8 | 27.1 | 30.1 | 32.8 | 35.3 | 37.7 | 39.9 | 36.2 | 18.5 | 0.7 | 0.3 | 0.9 | 1.8 |

The full grid, at every tenth of a code, is in `implementation-design/candidate1_black_join.txt`.

**Two readings of the table.**
- Inside the interval (up to code 0.765), the amendment removes the blend's hump. The hump peaked
  at 177.0 on light active and 53.6 on dark receded, and the amended curve is at most the end's
  value.
- Between the end and code 1 the old solve still falls steeply: dark receded goes from 39.9 at
  code 0.7 to 0.7 at code 1.0. That is the measured-region response, and it is untouched.

**A correction to the finding this ruling answers.** The finding quoted receded dark as 20 → 216 →
12.4 → 0.2. That profile came from the CSS algebra test's receded material, which applied the
receded difference over the renderer's default instead of over the active document. The declared
`landed_T` reads 20 → 53.6 → 0.7 → 0.2 (above). Active light's 132 → 177 was read on a correctly
composed material and stands. Composing the receded endpoints correctly in that test is part of
this implementation.

## 5. The executable form

`implementation-design/candidate1_black_join.py` wraps the hashed `landed_T` and never edits a G0
file:
- `bridge(tone, e, A)` applies §2 to any tone over arguments;
- `landed_T(ep, scale, component, A)` is the amended candidate 1;
- `landed_at(e, sizeK, A)` is the same arithmetic per argument list, asserted equal to `landed_T`
  on each component's pixels.

Its report is `implementation-design/candidate1_black_join.txt`, and it writes the fixture the
runtime's CPU reference is held to, `implementation-design/fixtures/landed-bridged.json`.
