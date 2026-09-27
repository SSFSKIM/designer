W41 G1 step3 — spatial finding, no leaf (clause6, Decision Log6, §5.192)

Replay
OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 /tmp/w39-g2-wgpu/bin/python \
  read-spatial-v2.py ../body/report-1/spatial-selection.json NEW_OUTPUT_DIRECTORY
Archive root is ../archive-root.txt, verified by fetch-archive before this read.
Only calibration is admitted, with the whole ~/vitrea-w39 tree denied. Sixteen
fixed gradient cells,768 separate device rows,48*scale pixels per row, all seven
repeats. No strip mask/domain/population or fitted body coefficient changed.

The first read stopped BEFORE fitting because archive pose 'rest' was grouped
literally rather than translated to the declaration's 'active'. Original source
read-spatial.py and read-attempt-1.txt remain. The additive read-spatial-v2.py maps
rest->active explicitly and rejects unknown poses; two regressions pass. The
successful numerical observations are attempt-2/, not a relabelled attempt1.
Three pre-fit synthetic spatial tests passed and reviewer-medium found no
material findings. A second scoped review checked the additive mapping and all
saved scores/observations without re-opening the archive: clean.

Body selection
No complete four-endpoint body family survived step2, so every spatial number
uses DIAGNOSTIC B1/E3, not a surviving body or a nominated material. F is the
sealed neutral curve; fitted chromatic coefficients are retained by hash.
On these achromatic inputs those gains are inert. S0 is fixed; S1/S2 use the
bounded16-start local LS and minimax procedure. All starts, ranks and singular
values are in fits.json; no local miss is called a certified family negative.

Minimax maxima over all rows/channels/repeats (codes; both scales separately
pass/fail alike). LS readings and every cell remain in summary.json/scores.json.gz.
endpoint             S0         S1         S2
light-active      4.181818   3.800000   2.221383
light-inactive    1.916667   1.009174   1.009174
dark-active       3.272727   3.069272   2.007615
dark-inactive     2.666667   1.000000   1.000000
Only dark-inactive S1/S2 meet the one-code per-row calibration bound. The
light-inactive1.009174 miss stays a miss; no tolerance is rounded or widened.

Reflection and resolution
Reflected equal-input native rows differ by up to4 codes light active and3 dark
active on the whole declared >=6px strip at both scales; inactive differences
are <=1. These are observations, not fitted-family separations. None of the
fitted instance pairs separates by3 codes; largest is2.299977 (light-active
S1/S2). Inactive S0/S1 separates1.150612 light /2.034187 dark, still insufficient
resolution. This says nothing about S0 passing: its residual fails in every
stratum. All twelve instance comparisons and all reflected rows are retained.

Interpretation and limits
One mean and amplitude cannot separate a group/local blend from wide blur.
The signed active term is positional, not an identified lighting frame; a long
boundary tail remains an alternative even on this pinned strip. S2 improves the
active residual but does not close it. The archive has ZERO structured held-out
cells, so no spatial candidate can close or become a W41 leaf. A future native
bed must vary group mean/frequency and hold out structured backdrops before any
such operator can be adopted. No browser, holdout, CSS claim or material change.
