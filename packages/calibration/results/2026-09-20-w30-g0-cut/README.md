# W30 G0 — the cut and the declarations

**Gate: W30 G0, acceptance clauses 1, 2 and 3; contracts X1, X2, X4; Decision Log 1 (a), (b), (f).
Claims §5.156.**

No material constant, profile document, native fixture, golden, bound, floor or row of
`results/matrix.json` moves at this gate, and **no capture of any kind was taken**. Every number
here is a cut of evidence W29 committed. Nothing under `results/2026-09-16-w29-freeze/` is touched:
the charter's v1 had this child add an exemption reader to `freeze.py` and v2 withdrew it, so the
frozen documents stay byte-identical for the whole wave and `freeze.py verify` reads **1,818 entries
intact** at this gate's open and at its close.

## The files

| file | what it is |
| --- | --- |
| `resolve-pre-wave.ts` | writes the two files below through the fingerprint's own path, and refuses to write one whose digest is not the document's recorded `resolvedMaterialSha256` |
| `resolved-26.5-{light,dark}.json` | the **fully resolved** macOS 26.5 materials, canonicalised with keys sorted, committed before any leaf of either operator exists. 113 leaves each. Digests: `b2b570e4adcea8fb` and `874be66ea501621b` |
| `shadow-cut.py` / `.txt` / `.json` | the σ cut: per span per scale per scheme per backdrop class, gated sets and probe ladder apart, the thin-regime hypothesis tested on 102 cell pairs, the instrument on composites, the fit/check roster |
| `reach-table.ts` / `.txt` | the reach `outerShadowReachPx` implies at the shipped σ against the native σ and against the law, through the renderer's own functions, with the rejected device-px alternative beside it |
| `structure-cut.py` / `.txt` / `.json` | the structure cut: `interiorStdDev` per pitch per scheme per tier per span, active and inactive, macOS 26.5 and macOS 27, plus the scale comparison, the contrast discriminator and `sizeToneLevelFar`'s sign |
| `holdout-drop-check.py` / `.txt` | the proof that no reader built on `fit.py`'s `cells()` yields a holdout number without `--with-holdout`, exercised on a scratch matrix that contains one |
| `bounds-declaration.md` | the declarations, committed before G2 opens: the 27 tables unchanged and no floor, the five per-operator acceptances with their statistics and their fates, the claimed rows with lever and tier, the expected-unmoved and reported-not-claimed rows |
| `departure-stat.py` / `.txt` / `.json` | **added by the review closure** (Decision Log 3 (a), claims §5.156 §9): B3's stop condition computed from the committed matrix rather than quoted — the mean absolute exterior departure per tier, per profile and pooled, with the partition sweep that shows §5.154 §3's 0.00074 is not reproducible from this file |

## The tests this gate adds

- `test/w30-operator-identity.test.ts` — resolves each macOS 26.5 document today, removes the paths
  named in the exported `W30_OPERATOR_LEAVES` from both sides and deep-equals the rest to the
  committed pre-wave JSON. **Empty list, green today**: the proof is written before the commit it
  judges, so G2 cannot write its own.
- `test/adopted-thresholds.test.ts`, at the foot — the **1,107** gated macOS 26.5 row pin, and that
  those rows name exactly the two frozen documents. `atAShippedDocument` hashes the documents'
  bytes, so a digest re-recorded in place would empty the macOS 26.5 half of every bound and pass.
- `test/tier-coherence.test.ts`, at the foot — the CSS tier's measured structure attenuation, twelve
  recorded readings plus the relation they encode, read live off the matrix so that a fit which
  moves it is seen.

## Reproducing

```bash
npx tsx results/2026-09-20-w30-g0-cut/resolve-pre-wave.ts
python3 results/2026-09-20-w30-g0-cut/shadow-cut.py     > results/2026-09-20-w30-g0-cut/shadow-cut.txt
npx tsx results/2026-09-20-w30-g0-cut/reach-table.ts    > results/2026-09-20-w30-g0-cut/reach-table.txt
python3 results/2026-09-20-w30-g0-cut/structure-cut.py  > results/2026-09-20-w30-g0-cut/structure-cut.txt
python3 results/2026-09-20-w30-g0-cut/departure-stat.py > results/2026-09-20-w30-g0-cut/departure-stat.txt
python3 results/2026-09-20-w30-g0-cut/holdout-drop-check.py
python3 results/2026-09-16-w29-freeze/freeze.py verify
```

The review closure (2026-09-20) re-ran `shadow-cut.py`, `structure-cut.py` and
`holdout-drop-check.py`: every figure the first run recorded reproduces unchanged, and the three
outputs gain sections rather than losing any (`shadow-cut.txt` §9 and §10, `structure-cut.txt`'s
computed row counts and its sRGB-code column, `holdout-drop-check.txt`'s `render` block).
`structure-cut.py`'s scale comparison also gained the scene id as its last sort key, because the set
iteration it relied on is hash-randomised per process and made two runs differ in line order while
every figure agreed.

## The four things a later child should read first

1. **The macOS 27 generation of the matrix carries no probe row**, so the pitch ladder has no
   committed macOS 27 web reading. It is why the scatter's shape cannot be chosen here, why
   `sizeToneLevelFar` stays declined, and a decision for G4's canonical read (claims §5.156 §3).
2. **The thin shadow regime is the instrument, not Apple's law** — the (amplitude, σ) pair trades at
   a constant product and the fitted σ bifurcates on the author's tint. The floor is CSS px and its
   value is declared unfitted (claims §5.156 §2).
3. **The shipped σ is a third too NARROW at spans 128 and above**, so the reach grows 37 % at span
   160. X8's recomputation is not only a shrink (claims §5.156 §2).
4. **Span 130 has no fittable cell on any bed** and the accessibility profiles have none above span
   96, so both arrive by extrapolation — and one of the two `ssimMean` rows this wave claims is at
   span 130 (claims §5.156 §2, §5).
