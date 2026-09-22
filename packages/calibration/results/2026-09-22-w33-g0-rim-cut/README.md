# W33 G0 — the rim cut and declarations

Claims §5.170; no material change, capture, seal or holdout configuration read. This gate
establishes two referees and rejects a premature choice of stroke model. **G1 needs DL2 and a
settled colour/orientation law before fitting.** A constant amplitude and width are not yet
shown sufficient by the bytes.

## Evidence

- `referee.py`, `rules.py`, `referee.json`, `referee.txt`: native-only archival inventory;
  nine-black-backdrop non-holdout referee in two exterior conventions; exact SDF-shell stroke
  referee with all four corner arcs, per-channel absolute errors, offsets2–6, native/web notches
  on27 and frozen26.5; diagnostic families in encoded and linear sRGB. The eight colour fits
  are diagnostics of the existing residual, never renderer fits. The capture/matrix provenance
  and shipped document hashes are checked before any27 fitting capture is opened.
- `forms.ts`, `forms.json`, `forms.txt`: four counterfactual finished RGBA composites and a
  minimum-alpha oracle, using the production metric functions. All original shape readings
  reproduced exactly on380 non-holdout pairs; no pixels written to either capture tree.
- `tables.py`, `tables.json`, `tables.txt`:304 stratified numeric ceilings by a fixed rounding
  rule; the bed×span black-floor table, pitch ladder, native control, conditionality and26 M2
  ring intersections. `bounds-declaration.md` is the human declaration, pinned by SHA in tests.
- `identity-proof.ts`, `.json`, `.txt`: live-material proof for both frozen and four27 digests,
  flat gated leaves versus a nested empty container. Nothing under `src/` is edited.
- `b3-stop.txt`: predecessor stop rerun on its committed cut. `halo.txt`: explicitly requested
  archival predecessor corroboration, max137.10 and inactive0, not a new holdout evaluation.
- `browser-runs.txt`: opening isolation proof finished **2026-09-22T06:12:07Z**, **17/17** on
  chromium-gpu, **run by the parent after the worktree was built**;6.8s. RT0,IC0,
  NSGlassTintAmount0.5 read immediately before. Foreign-process count and idle interval were
  **unrecorded**, not inferred. Worker’s earlier attempt failed before tests because dist
  dependencies were absent. No other browser run.

## Census correction, preserved beside the memo

The committed full-exterior inventory is **448 cells,264 with native-black exterior pixels**,
including30 held-out cells with black; **14,329,648** pixels under this script's declared bbox
and far-exclusive convention. The memo's **14,325,464** is **unreproduced**, lower by4,184.
Its author confirmed that total came from an unverified helper. Do not silently replace it or
attribute the difference to an unproved mechanism.

| attempted full-exterior convention | native-black pixels |
| --- | ---: |
| committed: outside when x<x0 or x>=x1 or y<y0 or y>=y1 |14,329,648|
| far bound inclusive: x>x1 / y>y1 |14,295,374|
| far bound one pixel inward: x>=x1-1 / y>=y1-1 |14,343,649|
| one-device-pixel expanded box, both sides |14,261,258|

All these are inventory with no backdrop-black eligibility test, unlike referee A. The toolbar
bbox is156×44; stack inventory uses120×56 overlay at offset[0,-8]. Neither is a union stroke
model. Four `dark-solid` inactive tinted capsules carry680 native-black exterior pixels, over a
NONBLACK backdrop; two are holdout, two calibration. They are explicitly outside A's nine
backgrounds, not silently counted as backdrop black.

**The lift claim's native-only inventory reproduces exactly:**27 1x light67 cells/1,546,726
backdrop-black pixels and dark50/1,099,348, every pixel zero;26.5 light21 of69 and dark18 of56
cells have nonzero native pixels. The full exterior and offset>=2 backdrop-black inventories
are two different cuts; the memo placed them side by side without naming that difference.

## Reproduction

Run from any directory, replacing `$ROOT` by this checkout. Captures remain read-only.

```sh
export VITREA_WEB_CAPTURES=/Users/new/Developer/GitHub/designer/packages/calibration/web-captures
E="$ROOT/packages/calibration/results/2026-09-22-w33-g0-rim-cut"
python3.12 "$E/referee.py" --out /tmp/w33-cut
pnpm --dir "$ROOT" --filter @vitrea/calibration exec tsx "$E/forms.ts"
pnpm --dir "$ROOT" --filter @vitrea/calibration exec tsx "$E/identity-proof.ts"
python3 "$E/tables.py"
pnpm --dir "$ROOT" --filter @vitrea/calibration test
python3 "$ROOT/packages/calibration/results/2026-09-16-w29-freeze/freeze.py" verify
```

PIL and numpy are needed only by the raster reader (`python3.12` on the capture machine).
Unit tests of `rules.py` and the committed evidence need only standard-library Python.
`forms.ts`, `identity-proof.ts` and `tables.py` write beside themselves; use an isolated copy to
regenerate committed evidence rather than overwrite a historical record at a later generation.
Never run `--include-holdout` during candidate fitting. G1 alone owns its one post-seal inclusion.

## Limits

The finite bed identifies orientation×scheme×pose dependence, not a universal off-switch or a
colour law. In dark active `photo__capsule-button`, straight edges read-0.27 while corners read
about-20; a capsule-wide zero would erase a real residual. No tested global neutral/tinted
one-/two-parameter family reproduces all RGB channels across backdrops. Anisotropy and the
black-square brightening require more than a uniform black multiplier. Composite stroke
sampling is explicitly declined here; the forms experiment DOES use the exact declared union
for composites. No extrapolation to other dpr, IC-alone, dark accessibility, new geometry or
unseen backdrops is claimed. Frozen web controls are today's canonical captures, not proof of
the original frozen matrix's pixel generation; the native control and frozen hashes are distinct.
