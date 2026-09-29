W41 G1 E3 — actual rendered calibration/validation read (c9a §5.192)
===================================================================

The BODY candidate survives this complete calibration/validation rendered check.
This is not native holdout closure, a complete600 capture freeze, or authorization
to spend the archive receipt before the other wave candidates are determined.

Input: committed checkpoint9e328b6d, exactly536actual candidate cells (464calibration,
72validation), map SHA256 a642015018c1660bf1678c24671ae7c9c886d470f2f5eaf811fe8281c43da362.
Comparison: the committed full600 shipped-baseline map, restricted to these536.
The unchanged prepare.py render-calval command ran CPU-only against seven admitted
normal native run entries per cell through guarded calibration/validation Readers.
Content-identical states remained seven repeats. No browser or native holdout was
opened, and no pinned scorer, runtime or material source was edited.

Outcome
-------
130claimed uniform rendered cells meet every deep constraint:128measured plus
two censored cells with all bounds satisfied. Their worst uncensored deep error
is1code, exactly the declared floor. Four claimed-endpoint gradient cells retain
actual rendered deep diagnostics (not numericalS0); their deep error is0codes,
but that is not a spatial accuracy claim. All402identity endpoint PNGs are
byte-identical to their frozen shipped baseline.

There are zero claimeddeep, veto or identity failures. Every one of246632admitted
veto bins passes;43344population-deficient bins remain explicit exclusions.
The check retains5,919,168median/repeat/channel comparisons. Worst worsening is
exactly1code at light-inactive2x v270-c-c44__inactive, top straight, shell-1,
bin12,R, median (the full repeat rows remain in the raw record). The threshold is
worsening>1code, so this equality is admitted, not rounded into a smaller reading.
All other endpoint maxima of worsening are0 because they render at identity.

The unchanged runner.aggregate also accepts the complete576numerical+536rendered
raw score memberships and their mandatory status fields: numerical136measured+
2censored of138claimed; rendered128measured+2censored of130claimed. Unclaimed
counts438/406 remain diagnostics, not passes. This validation uses no receipt or
token. The raw reports, not the aggregate's passing boolean, retain the readings.

Important gaps retained
-----------------------
382raw deep cells miss their absolute bound, all unclaimed endpoint diagnostics.
The worst is125codes on dark-inactive red'sR channel, unchanged from shipped.
The E3 candidate claims no stroke or inner-edge fix. Its light-inactive absolute
edge residual still reaches55.5codes at1x g255-c-c44__inactive, arc bin0 shell0 R;
52codes at2x, and48codes at validation's g128 continuous rectangle side bin.
Those edge absolute scores are diagnostic; their W38 worsening veto still binds.
Structured rendered scores remain outside the uniform deep claim even when their
recorded error is small; a structured holdout remains deferred.

Per-stratum maxima (codes)
--------------------------
Endpoint | role | scale | backdrop | cells | rawdeep failures | deep maximum | worsening maximum | edge maximum
dark-active | calibration | 1x | linear-gradient | 2 | 2 | 7 | 0 | 50.375
dark-active | calibration | 1x | solid | 56 | 56 | 94 | 0 | 118
dark-active | calibration | 2x | linear-gradient | 2 | 2 | 7 | 0 | 46.9285714286
dark-active | calibration | 2x | solid | 56 | 56 | 94 | 0 | 122.571428571
dark-active | validation | 1x | solid | 9 | 9 | 14 | 0 | 68.2857142857
dark-active | validation | 2x | solid | 9 | 9 | 14 | 0 | 68.4137931034
dark-inactive | calibration | 1x | linear-gradient | 2 | 1 | 1.5 | 0 | 41.375
dark-inactive | calibration | 1x | solid | 56 | 51 | 125 | 0 | 125
dark-inactive | calibration | 2x | linear-gradient | 2 | 1 | 1.5 | 0 | 39
dark-inactive | calibration | 2x | solid | 56 | 51 | 125 | 0 | 125
dark-inactive | validation | 1x | solid | 9 | 6 | 11 | 0 | 59
dark-inactive | validation | 2x | solid | 9 | 6 | 11 | 0 | 59
light-active | calibration | 1x | linear-gradient | 2 | 2 | 7 | 0 | 50.625
light-active | calibration | 1x | solid | 56 | 55 | 73 | 0 | 77.2222222222
light-active | calibration | 2x | linear-gradient | 2 | 2 | 7 | 0 | 47.1428571429
light-active | calibration | 2x | solid | 56 | 55 | 73 | 0 | 78.7142857143
light-active | validation | 1x | solid | 9 | 9 | 11 | 0 | 62.8928571429
light-active | validation | 2x | solid | 9 | 9 | 11 | 0 | 62.8965517241
light-inactive | calibration | 1x | linear-gradient | 2 | 0 | 0 | 0 | 40.625
light-inactive | calibration | 1x | solid | 56 | 0 | 1 | 0 | 55.5
light-inactive | calibration | 2x | linear-gradient | 2 | 0 | 0 | 1 | 38.2857142857
light-inactive | calibration | 2x | solid | 56 | 0 | 1 | 0 | 52
light-inactive | validation | 1x | solid | 9 | 0 | 1 | 0 | 48
light-inactive | validation | 2x | solid | 9 | 0 | 1 | 0 | 48

Exact worst cell/member/part/side/shell/bin/channel/repeat witnesses are in
strata.json, not inferred from this compact table. It also distinguishes rawdeep
failures from claimed failures and reports all population exclusions.

Evidence and timing
-------------------
scores.json.gz preserves the unchanged scorer's full output. rendered-admission
was a2,455,641,994-byte duplicate-detail JSON; its lossless gzip has the original
byte count and SHA256 in admission-storage.json, with decompression verified.
No recorded number or flag was rewritten. veto.json retains all536veto booleans;
summary.json is the original scorer summary. reduction-source.txt is the exact
post-read streaming reduction, never a runtime/scorer/runner input; each complete
cell object is JSON-decoded before aggregation. Source provenance matches current
committed bytes. Independent result replay is reported separately.

The observable scoring interval was10:14:08.581329Z (directory creation after
validation) to10:42:50.047626Z (last output written),28m41.466s. These are filesystem
witnesses, not instrumented process-start/exit times. Exact finalCPU was not
recorded by the unchanged scorer. One midrun observation recorded22m38.20CPU at
26m42elapsed; timing.json retains it without promoting it to a final total.
A naive64/536proportional extrapolation gives205.55seconds for that CPU-workflow
portion only: it excludes browser work, numerical72scoring, receipt/verification,
and differences in geometry or contention. It is not an exposure duration promise.

Independent reviewer-high replay completed with no material findings. Its separate
streaming calculation reproduced all24strata and the exact membership, deep/rail
constraints,246632admitted/43344deficient bins and5,919,168veto comparisons.
It verified actual candidate/baseline PNG hashes, all28source witnesses and the
lossless admission storage proof at approximately120MiB peakRSS.
independent-replay.json records the findings and region counts.
