# W17 G1 — the `toolbar-group` residual, diagnosed and carried (Decision Log 5)

The re-form lands every other light cell on the renderer and leaves the two `toolbar-group`
scenes outside 0.005 against the GPU tier: **−0.0122 and −0.0150 at dpr 1, −0.0040 and −0.0101 at
dpr 2**. Decision Log 5 asked for a bounded diagnosis and nothing else. This is it.

## 1. The annulus profile, per surface, against the GPU tier

Each scene is three separate 46 × 46 capsules — circles, since the radius is the half extent.
The interior is split into four radial bands by the fraction of the half extent, and each band's
mean is differenced against the GPU tier's own capture of the same pixels.

| profile | scene | surface | 0.00–0.40 | 0.40–0.70 | 0.70–0.88 | 0.88–1.00 |
| --- | --- | --- | --- | --- | --- | --- |
| 1x light | `checkerboard` | first | −0.0053 | −0.0116 | −0.0066 | +0.0553 |
| 1x light | `checkerboard` | second | −0.0081 | −0.0107 | −0.0068 | +0.0172 |
| 1x light | `checkerboard` | third | −0.0043 | −0.0066 | −0.0119 | +0.0169 |
| 1x light | `photo` | first | −0.0050 | −0.0113 | −0.0170 | +0.0490 |
| 1x light | `photo` | second | −0.0074 | −0.0131 | −0.0137 | +0.0622 |
| 1x light | `photo` | third | −0.0078 | −0.0121 | −0.0135 | +0.0277 |
| 2x light | `checkerboard` | first | +0.0035 | +0.0059 | +0.0048 | +0.0573 |
| 2x light | `checkerboard` | second | +0.0039 | +0.0029 | −0.0012 | +0.0172 |
| 2x light | `checkerboard` | third | +0.0090 | −0.0005 | −0.0164 | +0.0103 |
| 2x light | `photo` | first | +0.0071 | +0.0013 | −0.0167 | +0.0357 |
| 2x light | `photo` | second | +0.0058 | +0.0014 | −0.0091 | +0.0532 |
| 2x light | `photo` | third | +0.0000 | −0.0036 | −0.0166 | +0.0140 |

Two readings. **The 1x deficit is a broad interior offset**, present at every depth from the centre
outward and roughly flat across the first three bands; it is not concentrated at the contour and it
is not a band artefact. **At 2x the core is positive and only the outer interior is negative**, so
whatever it is scales with something that changes between the scales — and what changes is the
heavy width in CSS px against the box: σ 13.8 on a 46 px box at dpr 1 (0.30 of it) and 4.46 at
dpr 2 (0.097).

## 2. The two derived residuals, evaluated on this geometry

`residuals.ts` was extended to the toolbar's own capsule and given a third model.

| cell | dpr | encoded-space mask mix | kernel truncation at the box | sum | measured |
| --- | --- | --- | --- | --- | --- |
| `toolbar-group` capsule | 1 | −0.003985 | −0.000352 | −0.004336 | **−0.0122** |
| `rrect-md` | 1 | −0.004082 | −0.000516 | −0.004597 | +0.0010 |
| `capsule-button` | 1 | −0.003981 | −0.000002 | −0.003983 | −0.0005 |
| `rrect-ml` | 1 | −0.004030 | +0.000247 | −0.003782 | −0.0003 |
| `toolbar-group` capsule | 2 | −0.002216 | +0.002147 | −0.000069 | **−0.0040** |
| `rrect-md` | 2 | −0.000946 | +0.000191 | −0.000755 | +0.0034 |
| `capsule-button` | 2 | −0.002175 | +0.000104 | −0.002071 | +0.0095 |
| `rrect-ml` | 2 | −0.000925 | +0.000191 | −0.000755 | +0.0039 |

**Neither model explains it.** The encoded-space mix of the two tinted layers is −0.0040 on the
toolbar capsule, which is the same value it takes on every other 1x cell — the ramp's heavy share
being high everywhere on a small capsule does not make it several times `rrect-md`'s, because the
affine scales the sharp–heavy difference by `1 − α` before the encode sees it either way. The
kernel's truncation at the element's own boundary — the third model, added because a
`backdrop-filter`'s input is the snapshot behind the border box and a kernel wider than the box is
sampling outside its own input whatever the filter's region says — is **−0.00035** at dpr 1 with
edge padding, two orders below the residual. The two together leave **−0.008 unexplained** at 1x.

## 3. The single-surface comparison the bed already carries

`checkerboard__capsule-button__rest` is a 122 × 46 capsule: the **same span**, the same material,
the same profile, the same ramp, one surface instead of three. It reads **−0.0005**. The toolbar's
46 × 46 capsules read −0.0122. The residual therefore does not track the span — which is what the
size law, the scatter facet, the band's derived light and the inner shadow's keep are all functions
of — and does track the box, its aspect, or the fact that three filtered elements sit 10 CSS px
apart on one page. A scratch scene of a lone 46 × 46 capsule would separate the last of those from
the first two, and it needs a native fixture the bed does not have.

## 4. Carried as a named gap

The residual is not explained by a derived term of this form, so it is recorded here rather than
attributed. **The gap: the CSS tier's interior on a surface whose box is small in both extents runs
0.012 to 0.015 below the GPU tier at dpr 1 and 0.004 to 0.010 at dpr 2, on a bed where every other
light cell lands inside 0.005.** Its evidence is §1's annulus profile — a broad interior offset,
scale-dependent, not at the contour — and §2's two models, which measure −0.004 of it. The shape of
the work that would close it is §3's: a lone small capsule against the same three-up arrangement,
which is a fixture this bed does not have and a capture the harness cannot synthesise.
