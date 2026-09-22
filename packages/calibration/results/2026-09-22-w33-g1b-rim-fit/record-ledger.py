#!/usr/bin/env python3
"""Land the measured W33 G1b records after the chain, never predict their totals (§5.172)."""
import json
from pathlib import Path
import re
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
read=lambda name:json.loads((HERE/name).read_text())
assert (HERE/'chain.txt').read_text().endswith('PASS\n')
rounds={n:read(f'rounds/{n}/stops.json') for n in ('pre-fit','A','B','R')}
seal=read('sealed-manifest.json')['documents']
m2=read('m2-rebaseline.json')['cells']
log=(HERE/'chain-test.txt').read_text()
tests=sum(map(int,re.findall(r'Tests\s+(\d+) passed',log)))
files=sum(map(int,re.findall(r'Test Files\s+(\d+) passed',log)))
assert tests==2715 and files==189
runs=(HERE/'browser-runs.txt').read_text().splitlines()
assert len(runs)==59 and all('RT=0 IC=0 slider=0.5 foreignProcessCount=0' in l and 'idleSeconds=60' in l for l in runs)
adopted=(ROOT/'packages/calibration/test/adopted-thresholds.test.ts').read_text()
predicate=re.search(r'const PREDICATE_EXCLUDES = \[(.*?)\] as const;',adopted,re.S)[1]
assert len(re.findall(r'^  "',predicate,re.M))==67
old=subprocess.check_output(['git','show','c0a3c1f9:packages/calibration/test/adopted-thresholds.test.ts'],cwd=ROOT,text=True)
assert predicate==re.search(r'const PREDICATE_EXCLUDES = \[(.*?)\] as const;',old,re.S)[1]
chunks=['''
## 5.172 W33 G1b: the lift stands down, the anchors compensate, and the holdout exposes the composite referee's domain (2026-09-22)

**Fit, seal and read complete; independent review pending.** W33 Decision Log1(a)/(d)
and Decision Log3 as RULED: the contour term stops at G1a's finding. Evidence is
`packages/calibration/results/2026-09-22-w33-g1b-rim-fit/`; branch `w33-g1b-rim-fit`.
Only the two ACTIVE macOS27 documents' lift amplitude and three thick anchors move.
No contour leaf, rim term, sigma law, length, thin anchor, policy amplitude, body,
chroma, tone, tint or scatter constant moves. No native capture or harness build.

### 1. The pre-fit bed reproduces, with an initial selection error kept visible

The declared bed is **386 WebGPU calibration/validation/probe cells**, six profiles,
with G0's **232 non-holdout black-floor cells** inside it. Shipped-byte scratch captures
reproduce every compared shadow field on every cell exactly: **386/386, zero native
and zero web differences**, not merely differences under a tolerance. C1, B1, B3,
the thin bands, both black masks and the probe halo equal the archival reader's values.
`pre-fit-repro.txt`, `reader-validation.txt`, and `rounds/pre-fit/` preserve the proof.

The first scratch runner was too broad: it selected six additional black-bearing
probe IDs and accessibility probes. It stopped on two undeclared RT probes with a
zero-length contour (`hc-text__rrect-lg__inactive`, `hc-text-28__rrect-md__inactive`).
Its **19 extra measured rows** remain in the raw scratch matrix and are named in
`prefit-diagnostic-only.json`; none enters a fit, stop, or canonical pass. The
completion run filled only missing declared identities and asserted every already
written row unchanged. `declared-bed.json` pins the intended identities. No scene
changed split, no holdout was opened during fitting, and no capture was taken at26.5.

### 2. A declaration, not a fitted zero

`liftAmplitude` is **0.001→0 on light and0.0005→0 on dark**. The measurement sits beside
it in each active document's `$comment`: Apple's27 exterior is zero on **67/50 cells,
1,546,726/1,099,348 backdrop-black pixels**, while the frozen26.5 control is nonzero on
**39/125 cells** and keeps **0.01/0.0051** and its digests (§5.170). Both receded
documents already held0 and are not rewritten. `liftSpanMin`, `liftSpanFull` and the
blur/shape leaves stay and are **unread at amplitude0**.

The handwritten `material.ts` change is a **doc comment only**. “Exactly zero over
black” holds for a uniformly black source, not every local black pixel: the lift
samples the sigma40 blurred chain at that pixel's position (`wgsl/optics.ts`'s
`outer_shadow_lift`, §5.65's S6). No runtime source value changes by hand; the selected
patch and digest changes in `macos27-profile.ts` are generated from the documents.

### 3. The rounds and every carried stop

A is lift0 with shipped anchors. B is A's closed-form window departure solve,
`anchor × departure_native / departure_web`, rounded to the existing four-decimal
anchor precision. R repeats B **unchanged**. All eight stop/diagnostic structures
reproduce exactly between B and R, and the canonical read's shadow fields then
reproduce B on all386 declared cells. Two fitted candidates and one repeat, within
the ten-round budget; no search for an unspecified minimum and no post-holdout fit.

| reading | C1 passing /12 | thin per-cell /206 | B1 /6 | B3, bound0.000056 | whole exterior, warning only | black >0 / >1 pixels | probe halo max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
''']
for label,r in rounds.items():
    chunks.append(f"| {label} | {sum(x['passStop'] for x in r['C1'])} | {sum(x['passStop'] for x in r['thin'])} | {sum(x['passStop'] for x in r['B1'])} | {r['B3']['value']:.10f} | {r['B3']['wholeExteriorWarning']:.10f} | {sum(x['integer']['aboveZero'] for x in r['black']):,} / {sum(x['integer']['aboveOne'] for x in r['black']):,} | {max(x['max'] for x in r['halo']):.6f} |\n")
chunks.append('''
**A breaks two C1 rows and B3; neither bound is widened.** B's constants below keep
them. B3's active half is0.0001092916→0.0002202087→0.0001001619; the81 inactive
rows remain exactly0 throughout. Both accessibility halves also stay exact. A's
break is therefore in the active standard material, not the recede or the policy.
B improves the pooled departure stop by8.35% from the shipped reading and leaves
8.41% of its unchanged bound unused. Every round's bed/pose decomposition is in
`stops.json`; `b3-sealed.txt` independently reruns W32 G2's adopted functional.

C1 is the upper-middle admitted-band T, bound **0.0042**, on the same twelve rows:

| bed / span | pre-fit | A | B = R = canonical |
| --- | ---: | ---: | ---: |
''')
for i,row in enumerate(rounds['B']['C1']):
    chunks.append(f"| {row['bed']} / {row['span']} | {rounds['pre-fit']['C1'][i]['value']:.8f} | {rounds['A']['C1'][i]['value']:.8f} | {row['value']:.8f} |\n")
chunks.append('''
B1 is unchanged in EVERY round: light sigma96/128/160 **8.9600/13.1648/17.3696**
inside **[8.8966,9.0193]/[12.6397,13.7947]/[16.7033,17.8198]**; dark
**9.0400/12.9280/16.8160** inside **[8.9084,9.3180]/[12.7458,13.8499]/[16.7931,18.3237]**.

**Thin passes, not unchanged.** A's206 band readings are exact. B/R's largest per-cell
increase is **0.000151**, `photo__toolbar-group__rest`,1x light,3–6, inside the
**0.002044** bar; all206 pass. One diagnostic order statistic moves **0.000091→0.000102**
at2x light/span44/6–12: **+0.000011**, with every constituent per-cell change inside
the bar. The older zero-tolerance order-statistic comparison is a diagnostic, not
an additional W33 stop; its `passStop` field in the copied-style round artifacts
names that comparison and must not be mistaken for the declared per-cell gate.
The mechanism is the existing thin/thick blend: `sizeThickness(44)=0.09228515625`,
whose second smoothstep gives the thick anchor **0.0239777479** weight. Unchanged
thin anchors do not isolate span44 from the96 anchor. Span32 stays exact.

### 4. The compensated anchors, and the near band that trades rather than stays identical

| leaf | light old→new | dark old→new |
| --- | --- | --- |
| thickOcclusionAt96 |0.0961→0.0870|0.1051→0.1038|
| thickOcclusionAt128 |0.1797→0.1650|0.2228→0.2188|
| thickOcclusionAt160 |0.2717→0.2518|0.3504→0.3443|

The span160 peak ENCODED-alpha reductions are **7.9983% light /1.9815% dark**, from
`1−(1−occlusion)^(1/2.4)` at the unchanged sizeGain0. The anchor's own linear-occlusion
reductions are7.3243%/1.7409%, different quantities. `compensation-units.json` replaces
the pre-fit5–7% estimate with these readings and does not repeat the old wrong-space
2.4% estimate.

The watched3–6 band is **not claimed identical**. Its absolute upper-middle residuals
are below; the largest increase is **+0.001065 at1x light/span128**, while that cell
stratum's full-window C1 improves0.00244529→0.00207371. This is a near/far trade, not
proof that every lit pixel loses nothing. No new zero-tolerance band bound is invented.

| bed / span | pre-fit | A | B = R |
| --- | ---: | ---: | ---: |
''')
for i,row in enumerate(rounds['B']['band3to6']):
    if row['span'] not in (96,128,160):continue
    chunks.append(f"| {row['bed']} / {row['span']} | {rounds['pre-fit']['band3to6'][i]['absoluteUpperMiddle']:.6f} | {rounds['A']['band3to6'][i]['absoluteUpperMiddle']:.6f} | {row['absoluteUpperMiddle']:.6f} |\n")
chunks.append('''
### 5. The black-floor referee, the dark declaration, and the holdout's five pixels

The declared non-holdout population has **232 cells,13,236,229 eligible pixels**,46
bed×pose×span groups. **138,390 web>0 pixels→0;477 web>1→0**, in both A and B/R,
under both G0 masks. The four light hc-text28/7 counts go **66/39 at1x and222/150
at2x→0**. All46 group fractions are0. Span160 remains probe-strength.

The dark amplitude IS separately visible in this controlled leaf-only reading:
**23,015 nonzero pixels on24 active dark cells→0 in A**, with anchors held. Its
non-holdout dark pooled fraction is **0.4208% over both poses**, or0.6054% active
only, not a silent rewrite of the memo's broader0.44%. The lit-pixel degeneracy
still does not identify a nonzero lift; the native black pixels declare0.

**Halo and holdout discipline.** The original `halo.py` cells are holdout. Each round
therefore uses its unchanged far-exterior statistic on non-holdout `checkerboard-8`
probe analogues;137.10 is retained as archival corroboration. At the one post-seal
holdout capture, the original checkerboard cells read WebGPU mean/max **0.88/6.11
at1x,0.83/6.12 at2x**, down from the archival1x11.98/137.10. Inactive mean/max stay0.
CSS reads **2.01/12.24 at1x,1.49/12.20 at2x**, with its old2.34/12.25 kept in W32.

**The zero target misses four composite HOLDOUT cells, recorded under X4.** Extending
G0's unchanged reader after the seal gives260 black-bearing cells,28 held out,
14,136,826 eligible pixels. Five one-byte pixels remain; web>1 stays0 everywhere:

|2x checkerboard glass-over-glass|web>0 /eligible|device coordinates|prior pixel RGB→now|
| --- | ---: | --- | --- |
|dark inactive|1/71,272|(142,329)|(1,1,1)→(1,1,1)|
|dark active|1/71,468|(142,70)|(1,1,1)→(1,1,1)|
|light inactive|2/71,272|(100,287),(142,329)|(1,1,1)→(1,1,1)|
|light active|1/71,227|(142,70)|(1,1,1)→(1,1,1)|

All five lie **inside the BASE box [50,35]–[270,165] and outside the OVERLAY box
[100,64]–[220,120]**. G0's composite `geometry()` names the56px overlay, so its
“exterior” admits base-edge pixels. Both integer and analytic masks inherit that
wrong component domain. Dark active's total count nevertheless falls2485→1 and
light active9871→1; inactive1/2 are unchanged. This is the composite referee's
domain miss, not a newly introduced lift outside the stack. The unchanged referee
STILL MISSES: the five pixels are not deleted, excused by a widened zero, or fitted
away. `holdout-composite-decomposition.json` records coordinates and both generations.
**G2 must correct the composite domain before adopting the zero row** (union box or
an explicit composite decline, as G0's stroke referee already does). No new native
capture, material change, holdout render or contour decision follows this finding.

### 6. The rule-2 seal and its sites

Seal commit **0d0594b2** carries `configuration.py record` as read4 BEFORE any pass.
Source-list hash remains`c16d6294a00c8ac770781701b2154d636c7b287490526d49f3782aa1d2102a9d`;
source hash is`c48b40b13135efa121c7be4d4b2de08c131438187e2276bea1d19b3928e09cdf`.
The source hash moved on the doc comment, not a shader/default change.

|endpoint|resolved digest old→new|file SHA-256 first12 old→new|
| --- | --- | --- |
''')
for scheme,pose in [('light','active'),('dark','active'),('light','receded'),('dark','receded')]:
    name=f'apple-macos-27.0-1x-{scheme}-standard-glass0.5'+('-receded' if pose=='receded' else '')+'.json'
    d=seal[name]
    chunks.append(f"|{scheme} {pose}|`{d['beforeDigest']}`→`{d['resolvedMaterialSha256']}`|`{d['beforeFileSha256'][:12]}`→`{d['fileSha256'][:12]}`|\n")
chunks.append('''
`sealed-manifest.json` carries all full SHA-256 values. The seal asserts both frozen
resolved digests **b2b570e4adcea8fb/874be66ea501621b** before writing, and asserts both
receded COMPOSED digests after applying the changed active endpoint. Receded files
are never written. The identity table and rule2 are unchanged; no supersession record.

`digest-sites.txt` states each site's claim, not only whether it reads a digest:
the two active documents/history; generated runtime profile; two active full hashes
in `window-activation.spec.ts` with their prior values retained; the canonical runner's
four file-hash refusal checks; and live README digest prose. Frozen selection, history
readers and composition tests keep their promises unchanged. Seal tests36/36.

### 7. The canonical read, split, conditioning and current witnesses

Exactly **786 rows appended**:332 calibration/validation,330 unchanged ladder,
124 holdout, the latter once by artifact. **1,893→2,679→1,893** working rows;
**509 light** move to`superseded/d5bdd6eac432.json`, **277 dark** to`431cabd391c4.json`.
The split records `--claims "c9a §5.172" --read-claims "c9a §5.168"`: mover and reader
are different gates. Both append-checks pass **6/6**, including byte reconstruction.
No26.5 row is changed or appended;1,107 remain. The19 diagnostic scratch rows are
not promoted. The capture tree is this worktree's, **786/786 match**, no mismatches,
misfiled, superseded, unreadable, no-row or missing captures among its live profiles.
The parent must copy it at merge and archive the previous tree under the active hashes.

`PREDICATE_EXCLUDES` remains **67**, byte-identical to its prior declaration and
machine-verified by its owner case. The gated count is **230/786**, plus229/1,107
frozen; no cell is smuggled out of a gate. C1 and M1/M2 cuts are regenerated here and
the tests re-derive their numbers from the matrix. `SHIPPED_DOCUMENT_HASHES` remains
derived from the files, not a hand-maintained list.

One existing recorded CSS miss reads **0.88421→0.88424** (`checkerboard__rrect-lg`,
1x light,SSIM mean); it still misses≥0.9. The missed SET remains the same eight rows
(five image metrics, three M1 cells); no M2 miss is added. Four standard structure
witnesses also move. `refresh-read-witnesses.py` derives their current readings and
keeps prior digits beside them. These are witness updates, not bound changes. The
initial suite reports five stale-witness failures; after refresh **644/644** pass.

### 8. M2, every gated cell's per-wave move and cumulative drift

W32 Decision Log4 advances the reference to the generation this read supersedes,
resolved through the index: light`d5bdd6eac432`, dark`431cabd391c4`. The2% bound is
unchanged and all26 cells pass. Cumulative drift is measured from W31's pre-fit
`d0c389d70456`/`880ab1e31450`, also via the index, not bounded away or reset. L/D mean
light/dark standard; all rows are untinted photo on the WebGPU tier. Full precision
and reference values are in`m2-rebaseline.json`; the mask is native-derived.

|bed|photo component /pose|reference stddev→current|per-wave %|cumulative %|
| --- | --- | --- | ---: | ---: |
''')
for r in m2:
    profile=r['profile']; bed=('2x' if '-2x-' in profile else '1x')+(' D' if '-dark-' in profile else ' L')
    name=r['scene'].removeprefix('photo__').replace('__',' / ')
    chunks.append(f"|{bed}|{name}|{r['waveReference']:.9f}→{r['value']:.9f}|{r['perWave']*100:+.6f}|{r['cumulative']*100:+.6f}|\n")
chunks.append('''
The worst per-wave move is **−0.039391%**,1x dark photo/md active. Twenty cells are
exactly unchanged. The old1x-light/small-inactive cumulative **−2.774796%** remains
visible while this wave's change on that cell is0. No body parameter was fitted.

### 9. The sheets and the eye

**17 sheets reviewed**, native|WebGPU|CSS|x8 before/after, with one-byte-at-black
**137.10/255** and actual counts beside EVERY difference panel. Photo/lg and capsule
cover both schemes/scales. The black-floor sheets cover hc-text28/7,checkerboard8
at128/160 and light impulse/md. Dark impulse/md has no native fixture and is declined
explicitly, not substituted. `eye.txt` records the observations and `sheet-readings.json`
the bytes/provenance. The first sheet pass stopped at that absent fixture; completion
asserted existing images pixel-identical before writing the remaining ones.

The mid-grey exterior checker and hc-text stripe glow disappear. The known contour
hairline and body/chroma/structure residuals remain. No new terrace or secondary edge
is visible in unamplified native/WebGPU exteriors; faint quantized level contours are
PRESENT in amplified residuals before and after, so “none anywhere” is not claimed.
**No new eye-only regression was found; the eye did not STOP the gate.** The holdout
composite miss is the separate metric finding in§5 above.

CSS's no-floor statement is **far-exterior/analytic-box qualified**. The integer
mask admits centres1.5CSSpx out: CSS counts170 on checker8/lg,134 on ml,165 on
hc-text28/lg and204 on light impulse/md, unchanged before/after. All have analytic
BOX-distance≥2 count0; their rounded-contour distances extend to2.77CSSpx. This
pre-existing near-edge geometry residual is not the WebGPU lift and is not closed
silently. `css-floor.json` records both masks and distances; the tracker carries it.

### 10. Verification and what this gate does not claim

''')
chunks.append(f"**Closing chain:** build/lint exit0; **{tests:,} unit tests in{files} files**,0 failed;\n")
chunks.append('''calibration644/644; renderer goldens **34/34**,13 PNGs byte-identical with no regen;
window-activation **6/6** on Chromium, including all eight endpoint hash readings;
freeze **1,818** at open/close; capture checker **786/786** again at close. All21
pinned document/source/fixture/golden files are byte-identical. `git diff --check`
passes. **59 browser invocations** each have RT0,IC0,slider0.5,foreign-process count0
and an explicit60-second idle interval recorded before the run, including the failed
undeclared scratch probe invocation. No browser suite overlaps a capture pass.

A minor`@vitreajs/vitrea-web` changeset names the native counts, compensated anchors,
four resolved/file hashes and unchanged26.5/receded documents. Versioning/publishing,
independent review, merge and capture-tree transfer belong to the parent/G2; none was
done here. `calibration.ts:187`'s lift-width sentence is flagged for G2.

This gate does **not** claim a contour law, a new rim, a universal zero over the
unchanged composite referee, an exactly unchanged3–6 band, a located fit minimum,
a CSS near-edge match, or closure of the photo body's known chroma/structure gap.
No identity-table leaf is added and no bound/floor is widened. The five composite
holdout pixels remain recorded misses until G2 fixes the referee's domain before
adoption. The later identifying contour capture remains Decision Log3's first
Deferred item, requiring its own native-capture authorization.
''')
path=ROOT/'docs/doperpowers/specs/c9a-fidelity-claims.md'
s=path.read_text(); assert '\n## 5.172 ' not in s
path.write_text(s+'\n'+''.join(chunks))
# Count the commit carrying this record, rather than being off by one at landing.
n=int(subprocess.check_output(['git','rev-list','--count','c0a3c1f9..HEAD'],cwd=ROOT,text=True))+1
assert n==2
path=ROOT/'docs/doperpowers/specs/2026-09-22-w33-rim-wave.md'; s=path.read_text()
old='| G1b | not opened (v4: the lift alone) |'
new='''| G1b | **FIT/SEAL/READ COMPLETE, REVIEW PENDING 2026-09-22** — §5.172; **two commits**, seal`0d0594b2` and the commit carrying this row (one existed before it, so this row lands as the second). Declared386-cell pre-fit exact; A removes the lift, B compensates only the three thick anchors, R repeats B exactly. C1 twelve/twelve, B1 six/six, thin206/206 under0.002044, B3=0.0000512877 under0.000056. Black floor232/232 non-holdout cells zero; **four composite holdout cells retain five unchanged base-edge pixels admitted by G0's overlay-only box**, recorded, not widened; G2 corrects that domain before adoption. Two active documents sealed, both receded and both frozen unchanged. Read786 appended, split786 with reader§5.168, working1893; both append-checks6/6, tree786/786, gated230/786, predicate67. M2 all26 pass, worst per-wave−0.039391%;17 sheets viewed, no new eye-only stop. Chain2,715/189 files, goldens34, activation6, freeze1,818. No contour leaf, rim move, native capture, merge or publish. |'''
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace('## Revision Notes\n','''## Revision Notes

- 2026-09-22 (G1b, §5.172): the lift-only route is executed under DL1(a)/(d) and
  DL3. B's compensated material meets all declared fitting stops and repeats
  exactly; the canonical read is sealed once and includes one holdout artifact.
  G0's overlay-only composite exterior mask admits five unchanged base-edge pixels
  on four2x holdout rows. That zero-target miss is kept, not fitted or widened;
  G2 owns the union-box/decline correction before adopting the referee. The thin
  order-statistic +0.000011 is diagnostic; the per-cell bar is met. Near3–6 bands
  trade while C1 passes, and CSS's no-floor statement is mask-qualified.

''',1)
s=s.replace('## Surprises & Discoveries\n','''## Surprises & Discoveries

- G1b (§5.172): the holdout's five one-byte pixels all sit INSIDE the base box of
  glass-over-glass and outside the overlay box G0 used as the whole component.
  Their bytes are unchanged from the prior generation, including the receded
  poses. The material's non-holdout lift floor closes; the composite referee's
  domain must be corrected by G2 before adoption, without deleting this reading.
- G1b: thick anchors reach span44 through the existing thin/thick blend (weight
  0.0239777479), so thin is bounded, not identical, despite unchanged thin anchors.
  The first scratch selection also overreached into undeclared probes;19 measured
  extras and two unmeasurable cells are retained as diagnostic-only and excluded
  from the386-cell fit and786-row canonical read.

''',1)
path.write_text(s)
path=ROOT/'docs/doperpowers/specs/2026-09-21-w32-shadow-wave.md'; s=path.read_text()
anchor='`b4-black-floor.py` and `halo.py` are the two readings.'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
   **Closed beside, W33 G1b,2026-09-22 (§5.172):** macOS27's lift is declared0,
   the three thick anchors compensate, and all232 declared non-holdout black-floor
   cells read0 under both masks. The holdout records five unchanged base-edge
   pixels on four composite rows admitted by an overlay-only referee box; this is
   a separate G2 instrument-domain correction before adoption, not a retained lift
   or a widened zero. Frozen26.5 keeps its measured lift. The sheets print the LSB
   check; no contour term was added under W33 DL3.
''',1)
path.write_text(s)
path=ROOT/'docs/doperpowers/specs/tech-debt-tracker.md'; s=path.read_text()
start=s.index('## Over a pure-black backdrop vitrea\'s exterior sits one byte above Apple\'s')
end=s.index('\n---',start)
closure='''

**Lift term closed beside,2026-09-22, W33 G1b (§5.172).** The two active macOS27
amplitudes are declared0 and the three thick anchors compensate under all stops;
232/232 non-holdout cells,13,236,229 eligible pixels, read0 under both masks.
The original statement and counts above remain their generation's evidence.
The four2x composite holdout rows retain five unchanged base-edge pixels because
G0's mask names the overlay box, not the stack. That zero-target miss is recorded
and remains an instrument task below, not a widened bound. The frozen26.5 material
keeps its lift. Every new sheet carries the LSB check;17 were viewed.
'''
s=s[:end]+closure+s[end:]
s+='''

---

## W33 G1b: correct the black-floor referee's composite domain before adoption

The post-seal holdout (§5.172; `holdout-composite-decomposition.json`) reads five
one-byte pixels on four2x `checkerboard__glass-over-glass` rows. All were1 before
and after. All lie inside base box[50,35]–[270,165], outside overlay box
[100,64]–[220,120]; G0's56px component surrogate calls base-edge pixels exterior.
The same mask makes dark active's count2485→1 and light active9871→1, while the
inactive counts1/2 stay. No new lift persists beyond the stack. **G2, before the
zero row is adopted:** read a union box or decline composites explicitly as the
stroke referee does; keep this held-out reading and show the corrected domain's
reading beside it, without a new capture or a fitted constant. The zero is not
widened and this is not an excuse to erase the five pixels from their first cut.

## W33 G1b: CSS near-edge black pixels are not its far-exterior lift floor

`css-floor.json` (§5.172) reads pre-existing, unchanged counts under G0's integer
mask: checkerboard8/lg170,ml134,hc-text28/lg165,light impulse/md204 at1x. The mask
admits centres1.5CSSpx outside the box; analytic BOX-distance>=2 reads0 for all,
while rounded-contour distance reaches2.77CSSpx. Thus the older far-halo “no floor”
claim is true on its domain, not a proof that CSS matches the near contour. This
is not the WebGPU lift and no CSS constant moved to hide it. Carry it into the
geometry-qualified CSS contour work, with both distance conventions explicit.

## W33 G2 prose follow-up: the demo's lift-width explanation no longer names its default

`apps/demo/src/site/calibration.ts:187` and its adjacent doc comment attribute the
thin-span fitted width to the lift. W33 G1b's default macOS27 material has lift0;
its shape leaves are unread. Correct that sentence at G2's landing, keeping the
fit-versus-material-sigma distinction without attributing a zero operator's width.
The footer is flagged here, not changed as part of the material seal.
'''
path.write_text(s)
(HERE/'record-checks.json').write_text(json.dumps(dict(unitTests=tests,testFiles=files,
    browserInvocations=len(runs),predicateExcludes=67,branchCommitsIncludingRecord=n),indent=2)+'\n')
print('Ledger, charter and tracker records written from verified artifacts.')
